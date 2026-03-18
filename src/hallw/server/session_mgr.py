import asyncio
import uuid

import socketio
from langchain_core.messages import BaseMessage

from hallw.tools.playwright.playwright_mgr import browser_disconnect
from hallw.utils import logger

from .session import Session


class SessionManager:
    def __init__(self):
        self.sessions: dict[str, dict[str, Session]] = {}

    def resolve_session_id(self, data) -> str | None:
        if isinstance(data, dict):
            session_id = data.get("session_id")
            if isinstance(session_id, str) and session_id.strip():
                return session_id
        return None

    def get_client_sessions(self, sid: str) -> dict[str, Session]:
        return self.sessions.setdefault(sid, {})

    def pick_session(self, sid: str, session_id: str | None) -> Session | None:
        client_sessions = self.sessions.get(sid, {})
        if session_id:
            return client_sessions.get(session_id)
        if len(client_sessions) == 1:
            return next(iter(client_sessions.values()))
        return None

    def ensure_session(
        self,
        sid: str,
        sio: socketio.AsyncServer,
        main_loop: asyncio.AbstractEventLoop,
        session_id: str | None = None,
        thread_id: str | None = None,
    ) -> tuple[Session, str]:
        resolved_session_id = session_id or str(uuid.uuid4())
        client_sessions = self.get_client_sessions(sid)
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

    async def shutdown_session(
        self,
        sid: str,
        session_id: str,
        sio: socketio.AsyncServer,
        emit_reset: bool = True,
    ) -> bool:
        client_sessions = self.sessions.get(sid)
        if not client_sessions:
            return False

        session = client_sessions.get(session_id)
        if not session:
            return False

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
            logger.info(f"[session={session_id}] Input tokens: {session.input_tokens}")
            logger.info(f"[session={session_id}] Output tokens: {session.output_tokens}")

        session.close()
        del client_sessions[session_id]
        if not client_sessions:
            self.sessions.pop(sid, None)

        if emit_reset:
            await sio.emit("reset", {"session_id": session_id}, room=sid)

        return True

    async def restore_session_from_history(
        self,
        sid: str,
        sio: socketio.AsyncServer,
        main_loop: asyncio.AbstractEventLoop,
        session_id: str,
        thread_id: str,
        messages: list[BaseMessage],
        stats: dict,
    ) -> Session:
        client_sessions = self.get_client_sessions(sid)
        existing_session = client_sessions.get(session_id)
        if existing_session:
            await self.shutdown_session(sid, session_id, sio, emit_reset=False)
            client_sessions = self.get_client_sessions(sid)

        session = Session(sid=sid, sio=sio, main_loop=main_loop, session_id=session_id, thread_id=thread_id)
        client_sessions[session_id] = session
        session.history = messages
        session.input_tokens = stats.get("input_tokens", 0)
        session.output_tokens = stats.get("output_tokens", 0)
        return session


# Singleton export
session_mgr = SessionManager()
