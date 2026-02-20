import asyncio
import uuid
from typing import Optional

import socketio
import uvicorn
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_litellm import ChatLiteLLM
from langgraph.checkpoint.base import BaseCheckpointSaver
from pydantic import SecretStr

from hallw.core import AgentEventDispatcher, AgentState, AgentTask
from hallw.server.socket_renderer import SocketAgentRenderer
from hallw.tools.playwright.playwright_mgr import browser_disconnect
from hallw.utils import config, get_system_prompt, history_mgr, init_logger, logger, save_config_to_env

# --- Global State ---
active_task: Optional[AgentTask] = None


class Session:
    def __init__(self, sid: str, task_id: Optional[str] = None):
        self.task_id = task_id if task_id else str(uuid.uuid4())
        self.renderer = SocketAgentRenderer(sio, sid)
        self.history = [SystemMessage(content=get_system_prompt())]
        self.input_tokens = 0
        self.output_tokens = 0


current_session: Optional[Session] = None

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = socketio.ASGIApp(sio)


def create_agent_task(user_task: str, sid: str, checkpointer: BaseCheckpointSaver) -> AgentTask:
    global current_session

    if not current_session:
        current_session = Session(sid)
    else:
        current_session.renderer.sid = sid

    # Always prepare the current message stack from history
    messages = current_session.history.copy()

    # Append the new user request
    user_msg = HumanMessage(content=f"User: {user_task}")
    messages.append(user_msg)
    current_session.history.append(user_msg)
    logger.info(f"User: {user_task}")

    # LLM Configuration
    llm = ChatLiteLLM(
        model=config.model_name,
        temperature=config.model_temperature,
        max_tokens=config.model_max_output_tokens,
        streaming=True,
        stream_usage=True,
        stream_options={"include_usage": True},
        model_kwargs={
            "reasoning_effort": config.model_reasoning_effort,
        },
    )

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
        dispatcher=AgentEventDispatcher(current_session.renderer),
        initial_state=initial_state,
        checkpointer=checkpointer,
        invocation_config=invocation_config,
    )


# --- SocketIO Events ---
@sio.event
async def start_task(sid, data):
    global active_task, current_session
    task_text = data.get("task")
    if not task_text:
        return

    # Instantiate the new task
    cp = await history_mgr.get_checkpointer()
    agent_task = create_agent_task(task_text, sid, cp)

    # Initialize logger for this task execution
    init_logger(current_session.task_id)

    active_task = agent_task

    # Immediately echo the user's message back to the UI
    await sio.emit("user_message", task_text, room=sid)

    # Update recent models list
    _save_recent_model()

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
            if active_task:
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

    await browser_disconnect()

    if active_task and active_task.is_running:
        try:
            await active_task.cancel()
        except Exception:
            pass

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
async def get_history(sid):
    """Returns a list of all saved conversation threads."""
    try:
        threads = await history_mgr.get_all_threads()
        await sio.emit("history_list", threads, room=sid)
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        await sio.emit("error", {"message": f"Failed to fetch history: {e}"}, room=sid)


@sio.event
async def load_history(sid, data):
    """Loads a specific conversation thread."""
    global current_session, active_task
    thread_id = data.get("thread_id")
    if not thread_id:
        return

    try:
        # 1. Stop current task if running
        if active_task and active_task.is_running:
            await active_task.cancel()

        # 2. Load thread via manager
        thread_data = await history_mgr.load_thread(thread_id)

        if not thread_data:
            await sio.emit("error", {"message": "Thread not found"}, room=sid)
            return

        # 3. Re-hydrate session
        current_session = Session(sid, task_id=thread_id)
        current_session.history = thread_data["messages"]

        # Restore stats
        stats = thread_data["stats"]
        current_session.input_tokens = stats.get("input_tokens", 0)
        current_session.output_tokens = stats.get("output_tokens", 0)

        # 4. Emit loaded data
        await sio.emit(
            "history_loaded",
            {
                "messages": thread_data["serialized_msgs"],
                "thread_id": thread_id,
                "toolStates": thread_data["tool_states"],
            },
            room=sid,
        )

    except Exception as e:
        logger.error(f"Failed to load history: {e}")
        await sio.emit("error", {"message": f"Failed to load history: {e}"}, room=sid)


@sio.event
async def delete_history(sid, data):
    """Deletes a conversation thread."""
    thread_id = data.get("thread_id")
    if not thread_id:
        return

    try:
        await history_mgr.delete_thread(thread_id)
        await sio.emit("history_deleted", {"thread_id": thread_id}, room=sid)
    except Exception as e:
        logger.error(f"Failed to delete history: {e}")
        await sio.emit("error", {"message": str(e)}, room=sid)


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
async def resolve_user_decision(sid, data):
    if current_session:
        current_session.renderer.on_resolve_user_decision(data["request_id"], data["status"], data["value"])


@sio.event
async def resolve_cdp_page(sid, data):
    if current_session:
        current_session.renderer.on_resolve_cdp_page(data.get("status", "error"))


@sio.event
async def disconnect(sid):
    """Handles the socket disconnect event."""
    global active_task
    print(f"Client disconnected: {sid}")
    if active_task:
        await active_task.cancel()
        active_task = None


# --- Helper Functions ---
def _save_recent_model():
    recent_models = list(config.model_recent_used)
    model_name = config.model_name
    if model_name in recent_models:
        recent_models.remove(model_name)
    recent_models.insert(0, model_name)
    recent_models = recent_models[:10]

    if recent_models != config.model_recent_used:
        config.model_recent_used = recent_models
        save_config_to_env({"model_recent_used": recent_models})


# --- Main ---
def main():
    """Main entry point for the Uvicorn server."""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
