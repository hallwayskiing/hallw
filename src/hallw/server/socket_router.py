import asyncio

import socketio
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import SecretStr

from hallw.core import AgentRunner, create_agent_state
from hallw.tools.playwright.playwright_mgr import reset_session_browser, set_session_browser
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

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


# ── Socket Events ────────────────────────────────────────────────────────────


@sio.event
async def start_task(sid, data):
    if not isinstance(data, dict):
        return
    task_text = data.get("task", "")
    file_paths: list[str] = data.get("file_paths", [])
    if not task_text.strip() and not file_paths:
        return

    main_loop = asyncio.get_running_loop()
    session, session_id = session_mgr.ensure_session(
        sid,
        sio,
        main_loop,
        session_id=session_mgr.resolve_session_id(data),
        thread_id=data.get("thread_id"),
    )

    if session.active_runner and session.active_runner.is_running:
        await sio.emit("fatal_error", {"session_id": session_id, "message": "A task is already running."}, room=sid)
        return

    if not session.messages:
        session.messages.append(SystemMessage(content=get_system_prompt()))
    session.messages.append(_build_human_message(task_text, file_paths, data.get("message_id")))

    init_logger(session.thread_id)

    echo = {"session_id": session_id, "task": task_text}
    if file_paths:
        echo["files"] = file_paths
    await sio.emit("user_message", echo, room=sid)

    session.task = asyncio.create_task(_run_agent(session, session_id, sid))


@sio.event
async def stop_task(sid, data=None):
    session = session_mgr.pick_session(sid, session_mgr.resolve_session_id(data))
    if session and session.task and not session.task.done():
        session.task.cancel()


@sio.event
async def reset_session(sid, data=None):
    requested = session_mgr.resolve_session_id(data)
    if requested:
        await session_mgr.shutdown_session(sid, requested, sio)
    else:
        for s_id in list(session_mgr.get_client_sessions(sid)):
            await session_mgr.shutdown_session(sid, s_id, sio)


@sio.event
async def get_config(sid):
    raw = config.model_dump()
    await sio.emit(
        "config_data",
        {k: (v.get_secret_value() if isinstance(v, SecretStr) else v) for k, v in raw.items()},
        room=sid,
    )


@sio.event
async def update_config(sid, data):
    try:
        save_config_to_env(data)
        await sio.emit("config_updated", {"success": True}, room=sid)
    except Exception as e:
        logger.error(f"Config update failed: {e}")
        await sio.emit("config_updated", {"success": False, "error": str(e)}, room=sid)


@sio.event
async def get_history(sid):
    try:
        await sio.emit("history_list", await history_mgr.get_all_threads(), room=sid)
    except Exception as e:
        logger.error(f"Fetch history failed: {e}")
        await sio.emit("error", {"message": str(e)}, room=sid)


@sio.event
async def load_history(sid, data):
    if not isinstance(data, dict) or not (thread_id := data.get("thread_id")):
        return
    session_id = session_mgr.resolve_session_id(data) or thread_id
    try:
        thread_data = await history_mgr.load_thread(thread_id)
        if not thread_data:
            await sio.emit("error", {"session_id": session_id, "message": "Thread not found"}, room=sid)
            return

        await session_mgr.restore_session_from_history(
            sid=sid,
            sio=sio,
            main_loop=asyncio.get_running_loop(),
            session_id=session_id,
            thread_id=thread_id,
            state=thread_data["state"],
        )
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
        logger.error(f"Load history failed: {e}")
        await sio.emit("error", {"session_id": session_id, "message": str(e)}, room=sid)


@sio.event
async def delete_history(sid, data):
    if thread_id := data.get("thread_id"):
        try:
            await history_mgr.delete_thread(thread_id)
            await sio.emit("history_deleted", {"thread_id": thread_id}, room=sid)
        except Exception as e:
            logger.error(f"Delete history failed: {e}")
            await sio.emit("error", {"message": str(e)}, room=sid)


@sio.event
async def delete_all_history(sid):
    try:
        await history_mgr.delete_all_threads()
        await sio.emit("all_history_deleted", room=sid)
    except Exception as e:
        logger.error(f"Delete all history failed: {e}")
        await sio.emit("error", {"message": str(e)}, room=sid)


@sio.event
async def resolve_confirmation(sid, data):
    session = session_mgr.pick_session(sid, session_mgr.resolve_session_id(data))
    if session:
        session.renderer.on_resolve_confirmation(data["request_id"], data["status"])


@sio.event
async def resolve_user_decision(sid, data):
    session = session_mgr.pick_session(sid, session_mgr.resolve_session_id(data))
    if session:
        session.renderer.on_resolve_user_decision(data["request_id"], data["status"], data["value"])


@sio.event
async def resolve_cdp_page(sid, data):
    session = session_mgr.pick_session(sid, session_mgr.resolve_session_id(data))
    if session:
        session.renderer.on_resolve_cdp_page(data.get("status", "error"))


@sio.event
async def edit_user_message(sid, data):
    if not isinstance(data, dict):
        return

    session_id = session_mgr.resolve_session_id(data)
    session = session_mgr.pick_session(sid, session_id)
    if not session:
        return
    if session.active_runner and session.active_runner.is_running:
        await sio.emit(
            "fatal_error",
            {"session_id": session_id, "message": "Cannot edit messages while a task is running."},
            room=sid,
        )
        return

    thread_id = data.get("thread_id") or session.thread_id
    message_id = data.get("message_id")
    new_content = str(data.get("content", ""))
    if not thread_id or not message_id:
        return

    target_index = next(
        (
            idx
            for idx, msg in enumerate(session.messages)
            if isinstance(msg, HumanMessage) and str(getattr(msg, "id", "") or "") == message_id
        ),
        -1,
    )
    if target_index < 0:
        await sio.emit("error", {"session_id": session_id, "message": "User message not found"}, room=sid)
        return

    original_msg = session.messages[target_index]
    _replace_human_message(original_msg, new_content)
    session.state = create_agent_state(session.messages[:target_index] + [original_msg])

    await history_mgr.delete_thread(thread_id)

    serialized_msgs, tool_states = history_mgr.serialize_messages(session.messages)
    await sio.emit(
        "history_loaded",
        {
            "session_id": session_id,
            "messages": serialized_msgs,
            "thread_id": thread_id,
            "toolStates": tool_states,
        },
        room=sid,
    )
    session.task = asyncio.create_task(_run_agent(session, session_id, sid))


@sio.event
async def disconnect(sid):
    for s_id in list(session_mgr.get_client_sessions(sid)):
        await session_mgr.shutdown_session(sid, s_id, sio, emit_reset=False)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _build_human_message(task_text: str, file_paths: list[str], message_id: str | None = None) -> HumanMessage:
    if not file_paths:
        return HumanMessage(content=task_text, id=message_id)
    if file_paths:
        blocks = []
        for path in file_paths:
            parsed = parse_file(path)
            if parsed:
                blocks.extend(parsed)
        blocks.append({"type": "text", "text": task_text or " "})
        return HumanMessage(content=blocks, additional_kwargs={"files": file_paths}, id=message_id)
    return HumanMessage(content=task_text, id=message_id)


def _replace_human_message(message: HumanMessage, new_content: str) -> None:
    if isinstance(message.content, list):
        message.content[-1]["text"] = new_content
    else:
        message.content = new_content


async def _run_agent(s: Session, s_id: str, sid: str):
    """Core agent execution — runs as an asyncio.Task on the main loop."""
    ctx_token = set_session_browser(s.browser)
    local_conn = None
    try:
        local_conn, cp = await history_mgr.create_local_checkpointer()
        runner_state = await _build_runner_state(s, cp)
        runner = AgentRunner.create(
            state=runner_state,
            thread_id=s.thread_id,
            renderer=s.renderer,
            checkpointer=cp,
        )
        s.active_runner = runner
        runner.task = asyncio.current_task()

        state = await runner.run()
        if state:
            s.state = state
        else:
            logger.error(f"Task returned no state. [session={s_id}]")

    except asyncio.CancelledError:
        logger.info(f"Task cancelled. [session={s_id}]")
        _emit_bg(sid, "task_cancelled", {"session_id": s_id})
    except Exception as e:
        logger.error(f"Task error [session={s_id}]: {e}")
        _emit_bg(sid, "fatal_error", {"session_id": s_id, "message": str(e)})
    finally:
        s.active_runner = None
        reset_session_browser(ctx_token)
        if local_conn:
            try:
                await local_conn.close()
            except Exception:
                pass


async def _build_runner_state(s: Session, checkpointer):
    checkpoint_tuple = await checkpointer.aget_tuple({"configurable": {"thread_id": s.thread_id}})
    if not checkpoint_tuple:
        return create_agent_state(list(s.messages))

    checkpoint_state = checkpoint_tuple.checkpoint.get("channel_values", {})
    checkpoint_messages = checkpoint_state.get("messages", [])
    if len(checkpoint_messages) > len(s.messages):
        return create_agent_state(list(s.messages))

    pending_messages = s.messages[len(checkpoint_messages) :]
    return create_agent_state(list(pending_messages))


def _emit_bg(sid: str, event: str, data: dict):
    """Fire-and-forget emit (safe to call from CancelledError handlers)."""
    try:
        asyncio.get_running_loop().create_task(sio.emit(event, data, room=sid))
    except RuntimeError:
        pass
