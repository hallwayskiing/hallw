import asyncio

import socketio
import uvicorn
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_litellm import ChatLiteLLM
from langgraph.checkpoint.base import BaseCheckpointSaver
from pydantic import SecretStr

from hallw.core import AgentEventDispatcher, AgentRunner, AgentState
from hallw.tools.playwright.playwright_mgr import browser_disconnect
from hallw.utils import config, history_mgr, init_logger, logger, save_config_to_env

from .session import Session

# --- Global State ---
sessions: dict[str, Session] = {}


def create_agent_runner(user_task: str, session: Session, checkpointer: BaseCheckpointSaver) -> AgentRunner:
    messages = session.history.copy()
    # Append the new user request
    user_msg = HumanMessage(content=user_task)
    messages.append(user_msg)
    session.history.append(user_msg)
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

    invocation_config: RunnableConfig = {
        "recursion_limit": config.model_max_recursion,
        "configurable": {
            "thread_id": session.thread_id,
            "renderer": session.renderer,
        },
    }

    return AgentRunner(
        task_id=session.thread_id,
        llm=llm,
        dispatcher=AgentEventDispatcher(session.renderer),
        initial_state=initial_state,
        checkpointer=checkpointer,
        invocation_config=invocation_config,
    )


# --- SocketIO Events ---

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


@sio.event
async def start_task(sid, data):
    task_text = data.get("task")
    if not task_text:
        return

    main_loop = asyncio.get_running_loop()

    # Get or create session
    if sid not in sessions:
        sessions[sid] = Session(sid, sio, main_loop)
    else:
        sessions[sid].renderer.sid = sid
        sessions[sid].renderer.main_loop = main_loop

    session = sessions[sid]

    # Initialize logger for this task execution
    init_logger(session.thread_id)

    # Immediately echo the user's message back to the UI
    await sio.emit("user_message", task_text, room=sid)

    # Update recent models list
    _save_recent_model()

    async def run_wrapper():
        local_conn = None
        try:
            # CREATE LOOP-BOUND CHECKPOINTER
            local_conn, cp = await history_mgr.create_local_checkpointer()

            # Instantiate the new task inside the target loop
            agent_runner = create_agent_runner(task_text, session, cp)
            session.active_runner = agent_runner

            agent_runner.task = asyncio.current_task()
            final_state = await agent_runner.run()
            if final_state and session:
                initial_count = len(session.history)
                new_messages = final_state["messages"][initial_count:]
                session.history.extend(new_messages)

                session.input_tokens += final_state["stats"].get("input_tokens", 0)
                session.output_tokens += final_state["stats"].get("output_tokens", 0)
            else:
                logger.error("Task failed or session lost.")
        except asyncio.CancelledError:
            logger.info("Task was cancelled.")
            asyncio.run_coroutine_threadsafe(sio.emit("task_cancelled", {}, room=sid), main_loop)
            if session.active_runner and getattr(session.active_runner, "task", None):
                session.session_loop.call_soon_threadsafe(session.active_runner.task.cancel)
        except Exception as e:
            logger.error(f"Task error encountered: {e}")
            asyncio.run_coroutine_threadsafe(sio.emit("fatal_error", {"message": str(e)}, room=sid), main_loop)
        finally:
            session.active_runner = None
            if local_conn:
                try:
                    await local_conn.close()
                except Exception as db_e:
                    logger.error(f"Error closing DB connection: {db_e}")

    # Dispatch to the persistent session thread
    asyncio.run_coroutine_threadsafe(run_wrapper(), session.session_loop)


@sio.event
async def reset_session(sid):
    session = sessions.get(sid)
    if not session:
        return

    # Properly shutdown playwright on the session string
    future = asyncio.run_coroutine_threadsafe(browser_disconnect(), session.session_loop)
    try:
        future.result(timeout=5.0)
    except Exception as e:
        logger.error(f"Browser disconnect failed: {e}")

    if session.active_runner and session.active_runner.is_running and getattr(session.active_runner, "task", None):
        try:
            session.session_loop.call_soon_threadsafe(session.active_runner.task.cancel)
        except Exception:
            pass

    if session.input_tokens > 0 and session.output_tokens > 0:
        logger.info(f"Input tokens: {session.input_tokens}")
        logger.info(f"Output tokens: {session.output_tokens}")
    session.close()

    # Complete tear down
    del sessions[sid]

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
    thread_id = data.get("thread_id")
    if not thread_id:
        return

    # Check for active session existing first
    session = sessions.get(sid)

    try:
        # 1. Stop current task if running
        if (
            session
            and session.active_runner
            and session.active_runner.is_running
            and getattr(session.active_runner, "task", None)
        ):
            session.session_loop.call_soon_threadsafe(session.active_runner.task.cancel)

        # 2. Load thread via manager
        thread_data = await history_mgr.load_thread(thread_id)

        if not thread_data:
            await sio.emit("error", {"message": "Thread not found"}, room=sid)
            return

        # 3. Re-hydrate session
        main_loop = asyncio.get_running_loop()

        # If a session exists, shut it down fully and wipe it to refresh it clean
        if session:
            session.close()

        session = Session(sid, sio, main_loop, thread_id=thread_id)
        sessions[sid] = session

        session.history = thread_data["messages"]

        # Restore stats
        stats = thread_data["stats"]
        session.input_tokens = stats.get("input_tokens", 0)
        session.output_tokens = stats.get("output_tokens", 0)

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
    session = sessions.get(sid)
    if session and session.active_runner and getattr(session.active_runner, "task", None):
        session.session_loop.call_soon_threadsafe(session.active_runner.task.cancel)


@sio.event
async def resolve_confirmation(sid, data):
    session = sessions.get(sid)
    if session:
        session.renderer.on_resolve_confirmation(data["request_id"], data["status"])


@sio.event
async def resolve_user_decision(sid, data):
    session = sessions.get(sid)
    if session:
        session.renderer.on_resolve_user_decision(data["request_id"], data["status"], data["value"])


@sio.event
async def resolve_cdp_page(sid, data):
    session = sessions.get(sid)
    if session:
        session.renderer.on_resolve_cdp_page(data.get("status", "error"))


@sio.event
async def disconnect(sid):
    """Handles the socket disconnect event."""
    print(f"Client disconnected: {sid}")

    session = sessions.get(sid)
    if session:
        if session.active_runner and getattr(session.active_runner, "task", None):
            session.session_loop.call_soon_threadsafe(session.active_runner.task.cancel)

        # Shutdown browser
        try:
            future = asyncio.run_coroutine_threadsafe(browser_disconnect(), session.session_loop)
            future.result(timeout=5.0)
        except Exception as e:
            logger.error(f"Browser disconnect failed during disconnect: {e}")

        session.close()
        del sessions[sid]


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
    app = socketio.ASGIApp(sio)
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
