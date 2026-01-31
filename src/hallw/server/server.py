import asyncio
import os
import signal
import uuid
from typing import Optional

import socketio
import uvicorn
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from pydantic import SecretStr

from hallw.core import AgentTask
from hallw.server.socket_renderer import SocketAgentRenderer
from hallw.tools import load_tools
from hallw.tools.playwright.playwright_mgr import browser_close
from hallw.utils import config, generateSystemPrompt, init_logger, logger

# --- Global State ---
initiated = False
task_id = None
active_task: Optional[AgentTask] = None
conversation_history = []
agent_renderer: Optional[SocketAgentRenderer] = None
tools_dict = load_tools()

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

        # Read user profile
        user_profile = ""
        try:
            with open("PROFILE", "r") as f:
                user_profile = f.read()
        except FileNotFoundError:
            user_profile = "User does not provide any profile information."

        # Create renderer and conversation history
        agent_renderer = SocketAgentRenderer(sio, sid)
        conversation_history = [SystemMessage(content=generateSystemPrompt(tools_dict, user_profile))]

        initiated = True
    else:
        # Update existing renderer with the current session ID in case of reconnection
        agent_renderer.sid = sid

    # Always prepare the current message stack from history
    messages = conversation_history.copy()

    # Append the new user request
    user_msg = HumanMessage(content=f"User: {user_task}")
    messages.append(user_msg)
    conversation_history.append(user_msg)
    logger.info(f"User: {user_task}")

    # LLM Configuration
    api_key = config.model_api_key.get_secret_value() if config.model_api_key else None
    llm = ChatOpenAI(
        model=config.model_name,
        base_url=config.model_endpoint,
        api_key=api_key,
        temperature=config.model_temperature,
        max_tokens=config.model_max_output_tokens,
        streaming=True,
        stream_usage=True,
    ).bind_tools(list(tools_dict.values()), tool_choice="auto")

    return AgentTask(
        task_id=task_id,
        llm=llm,
        tools_dict=tools_dict,
        renderer=agent_renderer,
        initial_state={"messages": messages, "task_completed": False},
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

    # Cancel any existing running task before starting a new one
    if active_task:
        active_task.cancel()

    # Instantiate the new task
    agent_task = create_agent_task(task_text, sid)
    active_task = agent_task

    # Immediately echo the user's message back to the UI
    await sio.emit("user_message", task_text, room=sid)

    async def run_wrapper():
        """Execution wrapper to run the agent and handle completion."""
        try:
            await asyncio.shield(agent_task._run())

            # Save final AI response to history for multi-turn memory
            if agent_renderer and agent_renderer._current_response:
                conversation_history.append(AIMessage(content=agent_renderer._current_response))

            # Notify frontend that the task is complete
            await sio.emit("task_finished", {}, room=sid)
        except asyncio.CancelledError:
            logger.info("Task was cancelled.")
        except Exception as e:
            logger.error(f"Task error encountered: {e}")
            await sio.emit("fatal_error", {"message": str(e)}, room=sid)

    # Start the agent task as a background asyncio Task
    agent_task._task = asyncio.create_task(run_wrapper())


@sio.event
async def reset_session(sid):
    """
    Completely resets the agent state and conversation history.
    """
    global initiated, active_task, conversation_history, agent_renderer, task_id

    await browser_close()

    if active_task:
        active_task.cancel()

    # Reset all global variables
    conversation_history = []
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
        from hallw.utils import save_config_to_env

        save_config_to_env(data)
        await sio.emit("config_updated", {"success": True}, room=sid)
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        await sio.emit("config_updated", {"success": False, "error": str(e)}, room=sid)


@sio.event
async def stop_task(sid):
    """Signals the agent to stop current execution immediately."""
    if active_task:
        active_task.cancel()


@sio.event
async def resolve_confirmation(sid, data):
    """Routes user safety approval back to the agent core."""
    if agent_renderer:
        agent_renderer.on_resolve_confirmation(data["request_id"], data["status"])


@sio.event
async def window_closing(sid):
    """Handles the window closing event."""
    os.kill(os.getpid(), signal.SIGINT)


def main():
    """Main entry point for the Uvicorn server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
