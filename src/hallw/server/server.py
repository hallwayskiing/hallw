import asyncio
import uuid
from typing import Optional

import socketio
import uvicorn
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_litellm import ChatLiteLLM
from langgraph.checkpoint.memory import MemorySaver
from pydantic import SecretStr

from hallw.core import AgentState, AgentTask
from hallw.server.socket_renderer import SocketAgentRenderer
from hallw.tools import load_tools
from hallw.tools.playwright.playwright_mgr import browser_close
from hallw.utils import config, generateSystemPrompt, init_logger, logger, save_config_to_env

# --- Global State ---
initiated = False
task_id = None
agent_renderer: Optional[SocketAgentRenderer] = None
tools_dict = load_tools()
active_task: Optional[AgentTask] = None
conversation_history = []
input_tokens = 0
output_tokens = 0

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = socketio.ASGIApp(sio)


def create_agent_task(user_task: str, sid: str) -> AgentTask:
    """
    Initializes the agent environment or updates the existing one for a new task.
    """
    global initiated, task_id, conversation_history, agent_renderer

    checkpointer = MemorySaver()

    # Initialization logic for the first run after start or reset
    if not initiated:
        task_id = str(uuid.uuid4())
        init_logger(task_id)

        # Create renderer and conversation history
        agent_renderer = SocketAgentRenderer(sio, sid)
        conversation_history = [SystemMessage(content=generateSystemPrompt(tools_dict))]

        initiated = True
    else:
        # Update existing renderer with the current session ID in case of reconnection
        agent_renderer.sid = sid

    # Always prepare the current message stack from history
    messages = conversation_history.copy()

    # Append the new user request
    builder_msg = SystemMessage(
        content="""
            Now build the stages for the user request.
            <rules>
            CRITICAL INSTRUCTIONS:
            1. You MUST call the `build_stages` tool exactly once.
            2. The `stages` list you provide must be clear, actionable, and in the correct order.
            3. Do NOT call any other tools. Only call `build_stages`.
            4. If the user request is simple, create only one stage to finish it quickly.
            </rules>
        """
    )
    user_msg = HumanMessage(content=f"User: {user_task}")
    messages.append(builder_msg)
    messages.append(user_msg)
    conversation_history.append(user_msg)
    logger.info(f"User: {user_task}")

    # LLM Configuration
    llm = ChatLiteLLM(
        model=config.model_name,
        api_base=config.model_endpoint,
        temperature=config.model_temperature,
        max_tokens=config.model_max_output_tokens,
        streaming=True,
        stream_usage=True,
        stream_options={"include_usage": True},
        model_kwargs={
            "reasoning_effort": "low",
        },
    ).bind_tools(list(tools_dict.values()), tool_choice="auto")

    # Build initial state
    initial_state: AgentState = {
        "messages": messages,
        "task_completed": False,
    }

    return AgentTask(
        task_id=task_id,
        llm=llm,
        tools_dict=tools_dict,
        renderer=agent_renderer,
        initial_state=initial_state,
        checkpointer=checkpointer,
    )


@sio.event
async def start_task(sid, data):
    """
    Triggered when the user sends a message.
    """
    global active_task
    task_text = data.get("task")
    if not task_text:
        return

    # Instantiate the new task
    agent_task = create_agent_task(task_text, sid)
    active_task = agent_task

    # Immediately echo the user's message back to the UI
    await sio.emit("user_message", task_text, room=sid)

    async def run_wrapper():
        global active_task, conversation_history, input_tokens, output_tokens
        """Execution wrapper to run the agent and handle completion."""
        try:
            final_state = await agent_task._run()
            if final_state:
                initial_count = len(conversation_history)
                new_messages = final_state["messages"][initial_count:]
                conversation_history.extend(new_messages)

                input_tokens += final_state["stats"].get("input_tokens", 0)
                output_tokens += final_state["stats"].get("output_tokens", 0)
            else:
                logger.error("Task failed to produce a final state.")
        except asyncio.CancelledError:
            logger.info("Task was cancelled.")
            await sio.emit("task_cancelled", {}, room=sid)
            await active_task.cancel()
        except Exception as e:
            logger.error(f"Task error encountered: {e}")
            await sio.emit("fatal_error", {"message": str(e)}, room=sid)
        finally:
            active_task = None

    # Start the agent task as a background asyncio Task
    agent_task._task = asyncio.create_task(run_wrapper())


@sio.event
async def reset_session(sid):
    """
    Completely resets the agent state and conversation history.
    """
    global initiated, active_task, conversation_history, agent_renderer, task_id, input_tokens, output_tokens

    await browser_close()

    if active_task:
        await active_task.cancel()

    if input_tokens > 0 and output_tokens > 0:
        logger.info(f"Input tokens: {input_tokens}")
        logger.info(f"Output tokens: {output_tokens}")

    # Reset all global variables
    conversation_history = []
    input_tokens = 0
    output_tokens = 0
    active_task = None
    task_id = None
    agent_renderer = None
    initiated = False

    await sio.emit("reset", room=sid)


@sio.event
async def get_config(sid):
    """
    Sends the current configuration to the client.
    Handles SecretStr serialization manually.
    """
    raw_config = config.model_dump()
    json_config = {}
    for k, v in raw_config.items():
        if isinstance(v, SecretStr):
            json_config[k] = v.get_secret_value() if v else ""
        else:
            json_config[k] = v

    await sio.emit("config_data", json_config, room=sid)


@sio.event
async def update_config(sid, data):
    """
    Updates the configuration and saves it to .env.
    """
    try:
        save_config_to_env(data)
        await sio.emit("config_updated", {"success": True}, room=sid)
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        await sio.emit("config_updated", {"success": False, "error": str(e)}, room=sid)


@sio.event
async def stop_task(sid):
    """Signals the agent to stop current execution immediately."""
    if active_task:
        await active_task.cancel()


@sio.event
async def resolve_confirmation(sid, data):
    """Routes user safety approval back to the agent core."""
    if agent_renderer:
        agent_renderer.on_resolve_confirmation(data["request_id"], data["status"])


@sio.event
async def resolve_user_input(sid, data):
    """Routes user input back to the agent core."""
    if agent_renderer:
        agent_renderer.on_resolve_user_input(data["request_id"], data["status"], data["value"])


@sio.event
async def disconnect(sid):
    """Handles the socket disconnect event."""
    global active_task
    print(f"Client disconnected: {sid}")
    if active_task:
        await active_task.cancel()
        active_task = None


def main():
    """Main entry point for the Uvicorn server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
