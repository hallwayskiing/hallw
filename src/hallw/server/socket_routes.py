import asyncio
import uuid

import socketio
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import SecretStr

from hallw.core import AgentRunner
from hallw.tools.playwright.playwright_mgr import browser_disconnect
from hallw.utils import config, get_system_prompt, history_mgr, init_logger, logger, save_config_to_env

from .session import Session

# --- Global State ---
sessions: dict[str, dict[str, Session]] = {}

# --- SocketIO Events ---

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


def _resolve_session_id(data) -> str | None:
    if isinstance(data, dict):
        session_id = data.get("session_id")
        if isinstance(session_id, str) and session_id.strip():
            return session_id
    return None


def _get_client_sessions(sid: str) -> dict[str, Session]:
    return sessions.setdefault(sid, {})


def _pick_session(sid: str, session_id: str | None) -> Session | None:
    client_sessions = sessions.get(sid, {})
    if session_id:
        return client_sessions.get(session_id)
    if len(client_sessions) == 1:
        return next(iter(client_sessions.values()))
    return None


def _ensure_session(
    sid: str, main_loop: asyncio.AbstractEventLoop, session_id: str | None = None, thread_id: str | None = None
) -> tuple[Session, str]:
    resolved_session_id = session_id or str(uuid.uuid4())
    client_sessions = _get_client_sessions(sid)
    if resolved_session_id not in client_sessions:
        client_sessions[resolved_session_id] = Session(
            sid=sid,
            sio=sio,
            main_loop=main_loop,
            session_id=resolved_session_id,
            thread_id=thread_id,
        )

    session = client_sessions[resolved_session_id]
    session.renderer.sid = sid
    session.renderer.main_loop = main_loop
    return session, resolved_session_id


async def _shutdown_session(sid: str, session_id: str, emit_reset: bool = True) -> bool:
    client_sessions = sessions.get(sid)
    if not client_sessions:
        return False

    session = client_sessions.get(session_id)
    if not session:
        return False

    # Shutdown browser tied to this session loop
    future = asyncio.run_coroutine_threadsafe(browser_disconnect(), session.session_loop)
    try:
        future.result(timeout=5.0)
    except Exception as e:
        logger.error(f"Browser disconnect failed: {e}")

    # Cancel in-flight task
    if session.active_runner and session.active_runner.is_running and getattr(session.active_runner, "task", None):
        try:
            session.session_loop.call_soon_threadsafe(session.active_runner.task.cancel)
        except Exception:
            pass

    if session.input_tokens > 0 and session.output_tokens > 0:
        logger.info(f"[session={session_id}] Input tokens: {session.input_tokens}")
        logger.info(f"[session={session_id}] Output tokens: {session.output_tokens}")

    session.close()
    del client_sessions[session_id]
    if not client_sessions:
        sessions.pop(sid, None)

    if emit_reset:
        await sio.emit("reset", {"session_id": session_id}, room=sid)

    return True


@sio.event
async def start_task(sid, data):
    if not isinstance(data, dict):
        return

    task_text = data.get("task")
    if not task_text:
        return

    main_loop = asyncio.get_running_loop()
    requested_session_id = _resolve_session_id(data)
    thread_id = data.get("thread_id")
    session, session_id = _ensure_session(sid, main_loop, session_id=requested_session_id, thread_id=thread_id)

    if session.active_runner and session.active_runner.is_running:
        await sio.emit(
            "fatal_error",
            {"session_id": session_id, "message": "A task is already running in this session."},
            room=sid,
        )
        return

    # Init system message if not exists
    if not session.history:
        session.history.append(SystemMessage(content=get_system_prompt()))

    # Append the new user request
    user_msg = HumanMessage(content=task_text)
    session.history.append(user_msg)

    # Initialize logger for this task execution
    init_logger(session.thread_id)

    # Immediately echo the user's message back to the UI
    await sio.emit("user_message", {"session_id": session_id, "task": task_text}, room=sid)

    # Update recent models list
    _save_recent_model()

    async def run_wrapper(target_session: Session, target_session_id: str):
        local_conn = None
        try:
            # CREATE LOOP-BOUND CHECKPOINTER
            local_conn, cp = await history_mgr.create_local_checkpointer()

            # Instantiate the new task inside the target loop
            agent_runner = AgentRunner.create(
                messages=target_session.history.copy(),
                thread_id=target_session.thread_id,
                renderer=target_session.renderer,
                checkpointer=cp,
            )
            target_session.active_runner = agent_runner

            agent_runner.task = asyncio.current_task()
            final_state = await agent_runner.run()
            if final_state:
                initial_count = len(target_session.history)
                new_messages = final_state["messages"][initial_count:]
                target_session.history.extend(new_messages)

                target_session.input_tokens += final_state["stats"].get("input_tokens", 0)
                target_session.output_tokens += final_state["stats"].get("output_tokens", 0)
            else:
                logger.error(f"Task failed or session lost. [session={target_session_id}]")
        except asyncio.CancelledError:
            logger.info(f"Task was cancelled. [session={target_session_id}]")
            asyncio.run_coroutine_threadsafe(
                sio.emit("task_cancelled", {"session_id": target_session_id}, room=sid), main_loop
            )
            if target_session.active_runner and getattr(target_session.active_runner, "task", None):
                target_session.session_loop.call_soon_threadsafe(target_session.active_runner.task.cancel)
        except Exception as e:
            logger.error(f"Task error encountered [session={target_session_id}]: {e}")
            asyncio.run_coroutine_threadsafe(
                sio.emit("fatal_error", {"session_id": target_session_id, "message": str(e)}, room=sid), main_loop
            )
        finally:
            target_session.active_runner = None
            if local_conn:
                try:
                    await local_conn.close()
                except Exception as db_e:
                    logger.error(f"Error closing DB connection: {db_e}")

    # Dispatch to the persistent session thread
    asyncio.run_coroutine_threadsafe(run_wrapper(session, session_id), session.session_loop)


@sio.event
async def reset_session(sid, data=None):
    requested_session_id = _resolve_session_id(data)
    client_sessions = sessions.get(sid, {})

    if requested_session_id:
        await _shutdown_session(sid, requested_session_id, emit_reset=True)
        return

    # Backward-compatible fallback: reset every session for this client
    for session_id in list(client_sessions.keys()):
        await _shutdown_session(sid, session_id, emit_reset=True)


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
    """Loads a specific conversation thread into a target session."""
    if not isinstance(data, dict):
        return

    thread_id = data.get("thread_id")
    if not thread_id:
        return

    session_id = _resolve_session_id(data) or thread_id

    try:
        # 1. Load thread via manager
        thread_data = await history_mgr.load_thread(thread_id)

        if not thread_data:
            await sio.emit("error", {"session_id": session_id, "message": "Thread not found"}, room=sid)
            return

        # 2. Re-hydrate target session only
        main_loop = asyncio.get_running_loop()
        client_sessions = _get_client_sessions(sid)
        existing_session = client_sessions.get(session_id)
        if existing_session:
            await _shutdown_session(sid, session_id, emit_reset=False)
            client_sessions = _get_client_sessions(sid)

        session = Session(sid, sio, main_loop, session_id=session_id, thread_id=thread_id)
        client_sessions[session_id] = session
        session.history = thread_data["messages"]

        # Restore stats
        stats = thread_data["stats"]
        session.input_tokens = stats.get("input_tokens", 0)
        session.output_tokens = stats.get("output_tokens", 0)

        # 3. Emit loaded data
        await sio.emit(
            "history_loaded",
            {
                "session_id": session_id,
                "messages": thread_data["serialized_msgs"],
                "thread_id": thread_id,
                "toolStates": thread_data["tool_states"],
            },
            room=sid,
        )

    except Exception as e:
        logger.error(f"Failed to load history: {e}")
        await sio.emit("error", {"session_id": session_id, "message": f"Failed to load history: {e}"}, room=sid)


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
async def stop_task(sid, data=None):
    """Signals the agent to stop current execution immediately."""
    session_id = _resolve_session_id(data)
    session = _pick_session(sid, session_id)
    if session and session.active_runner and getattr(session.active_runner, "task", None):
        session.session_loop.call_soon_threadsafe(session.active_runner.task.cancel)


@sio.event
async def resolve_confirmation(sid, data):
    session_id = _resolve_session_id(data)
    session = _pick_session(sid, session_id)
    if session:
        session.renderer.on_resolve_confirmation(data["request_id"], data["status"])


@sio.event
async def resolve_user_decision(sid, data):
    session_id = _resolve_session_id(data)
    session = _pick_session(sid, session_id)
    if session:
        session.renderer.on_resolve_user_decision(data["request_id"], data["status"], data["value"])


@sio.event
async def resolve_cdp_page(sid, data):
    session_id = _resolve_session_id(data)
    session = _pick_session(sid, session_id)
    if session:
        session.renderer.on_resolve_cdp_page(data.get("status", "error"))


@sio.event
async def disconnect(sid):
    """Handles the socket disconnect event."""
    print(f"Client disconnected: {sid}")

    client_sessions = sessions.get(sid, {})
    for session_id in list(client_sessions.keys()):
        await _shutdown_session(sid, session_id, emit_reset=False)

    sessions.pop(sid, None)


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
