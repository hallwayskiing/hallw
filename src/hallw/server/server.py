import asyncio
import uuid
from typing import Optional

import socketio
import uvicorn
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_litellm import ChatLiteLLM
from langgraph.checkpoint.memory import MemorySaver
from pydantic import SecretStr

from hallw.core import AgentEventDispatcher, AgentState, AgentTask
from hallw.server.socket_renderer import SocketAgentRenderer
from hallw.tools import load_tools
from hallw.tools.playwright.playwright_mgr import browser_close
from hallw.utils import config, generateSystemPrompt, init_logger, logger, save_config_to_env

# --- Global State ---
tools_dict = load_tools()
active_task: Optional[AgentTask] = None


class Session:
    def __init__(self, sid: str):
        self.task_id = str(uuid.uuid4())
        self.renderer = SocketAgentRenderer(sio, sid)
        self.history = [SystemMessage(content=generateSystemPrompt(tools_dict))]
        self.input_tokens = 0
        self.output_tokens = 0
        init_logger(self.task_id)


current_session: Optional[Session] = None

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = socketio.ASGIApp(sio)


def create_agent_task(user_task: str, sid: str) -> AgentTask:
    global current_session

    checkpointer = MemorySaver()

    if not current_session:
        current_session = Session(sid)
    else:
        current_session.renderer.sid = sid

    # Always prepare the current message stack from history
    messages = current_session.history.copy()

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
    current_session.history.append(user_msg)
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
        "stats": {
            "input_tokens": 0,
            "output_tokens": 0,
            "tool_call_counts": 0,
            "failures": 0,
            "failures_since_last_reflection": 0,
        },
        "current_stage": 0,
        "total_stages": 0,
        "stage_names": [],
        "task_completed": False,
    }

    invocation_config = {
        "recursion_limit": config.model_max_recursion,
        "configurable": {
            "thread_id": current_session.task_id,
            "renderer": current_session.renderer,
        },
    }

    return AgentTask(
        task_id=current_session.task_id,
        llm=llm,
        tools_dict=tools_dict,
        dispatcher=AgentEventDispatcher(current_session.renderer),
        initial_state=initial_state,
        checkpointer=checkpointer,
        invocation_config=invocation_config,
    )


@sio.event
async def start_task(sid, data):
    global active_task, current_session
    task_text = data.get("task")
    if not task_text:
        return

    # Instantiate the new task
    agent_task = create_agent_task(task_text, sid)
    active_task = agent_task

    # Immediately echo the user's message back to the UI
    await sio.emit("user_message", task_text, room=sid)

    async def run_wrapper():
        global active_task, current_session
        try:
            final_state = await agent_task._run()
            if final_state and current_session:
                initial_count = len(current_session.history)
                new_messages = final_state["messages"][initial_count:]
                current_session.history.extend(new_messages)

                current_session.input_tokens += final_state["stats"].get("input_tokens", 0)
                current_session.output_tokens += final_state["stats"].get("output_tokens", 0)
            else:
                logger.error("Task failed or session lost.")
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
    global current_session, active_task

    await browser_close()

    if active_task:
        await active_task.cancel()

    if current_session:
        if current_session.input_tokens > 0 and current_session.output_tokens > 0:
            logger.info(f"Input tokens: {current_session.input_tokens}")
            logger.info(f"Output tokens: {current_session.output_tokens}")

    # Reset session related globals
    current_session = None
    active_task = None

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
    if current_session:
        current_session.renderer.on_resolve_confirmation(data["request_id"], data["status"])


@sio.event
async def resolve_user_input(sid, data):
    if current_session:
        current_session.renderer.on_resolve_user_input(data["request_id"], data["status"], data["value"])


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
