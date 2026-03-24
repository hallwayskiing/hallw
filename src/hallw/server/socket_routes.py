import asyncio

import socketio
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import SecretStr

from hallw.core import AgentRunner
from hallw.utils import (
    config,
    get_system_prompt,
    history_mgr,
    init_logger,
    logger,
    parse_file,
    save_config_to_env,
)

from .session import Session
from .session_mgr import session_mgr

# --- SocketIO Events ---

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


@sio.event
async def start_task(sid, data):
    if not isinstance(data, dict):
        return

    task_text = data.get("task", "")
    file_paths: list[str] = data.get("file_paths", [])

    if not task_text.strip() and not file_paths:
        return

    main_loop = asyncio.get_running_loop()
    requested_session_id = session_mgr.resolve_session_id(data)
    thread_id = data.get("thread_id")
    session, session_id = session_mgr.ensure_session(
        sid, sio, main_loop, session_id=requested_session_id, thread_id=thread_id
    )

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

    # Build a single HumanMessage containing both text and files
    if not file_paths:
        message = HumanMessage(content=task_text)
    else:
        blocks = []
        if task_text:
            blocks.append({"type": "text", "text": task_text, "role": "user"})
        for path in file_paths:
            parsed_blocks = parse_file(path)
            if parsed_blocks:
                blocks.extend(parsed_blocks)
        message = HumanMessage(content=blocks, additional_kwargs={"files": file_paths})
    session.history.append(message)

    # Initialize logger for this task execution
    init_logger(session.thread_id)

    # Echo user message back to the UI (include absolute file paths)
    echo_data: dict = {"session_id": session_id, "task": task_text}
    if file_paths:
        echo_data["files"] = file_paths
    await sio.emit("user_message", echo_data, room=sid)

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
    requested_session_id = session_mgr.resolve_session_id(data)
    client_sessions = session_mgr.get_client_sessions(sid)

    if requested_session_id:
        await session_mgr.shutdown_session(sid, requested_session_id, sio, emit_reset=True)
        return

    # Backward-compatible fallback: reset every session for this client
    for session_id in list(client_sessions.keys()):
        await session_mgr.shutdown_session(sid, session_id, sio, emit_reset=True)


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

    session_id = session_mgr.resolve_session_id(data) or thread_id

    try:
        # 1. Load thread via manager
        thread_data = await history_mgr.load_thread(thread_id)

        if not thread_data:
            await sio.emit("error", {"session_id": session_id, "message": "Thread not found"}, room=sid)
            return

        # 2. Re-hydrate target session only
        main_loop = asyncio.get_running_loop()
        await session_mgr.restore_session_from_history(
            sid=sid,
            sio=sio,
            main_loop=main_loop,
            session_id=session_id,
            thread_id=thread_id,
            messages=thread_data["messages"],
            stats=thread_data["stats"],
        )

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
    session_id = session_mgr.resolve_session_id(data)
    session = session_mgr.pick_session(sid, session_id)
    if session and session.active_runner and getattr(session.active_runner, "task", None):
        session.session_loop.call_soon_threadsafe(session.active_runner.task.cancel)


@sio.event
async def resolve_confirmation(sid, data):
    session_id = session_mgr.resolve_session_id(data)
    session = session_mgr.pick_session(sid, session_id)
    if session:
        session.renderer.on_resolve_confirmation(data["request_id"], data["status"])


@sio.event
async def resolve_user_decision(sid, data):
    session_id = session_mgr.resolve_session_id(data)
    session = session_mgr.pick_session(sid, session_id)
    if session:
        session.renderer.on_resolve_user_decision(data["request_id"], data["status"], data["value"])


@sio.event
async def resolve_cdp_page(sid, data):
    session_id = session_mgr.resolve_session_id(data)
    session = session_mgr.pick_session(sid, session_id)
    if session:
        session.renderer.on_resolve_cdp_page(data.get("status", "error"))


@sio.event
async def disconnect(sid):
    """Handles the socket disconnect event."""
    print(f"Client disconnected: {sid}")

    client_sessions = session_mgr.get_client_sessions(sid)
    for session_id in list(client_sessions.keys()):
        await session_mgr.shutdown_session(sid, session_id, sio, emit_reset=False)
