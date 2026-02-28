import asyncio
import threading

import socketio
from langchain_core.messages import BaseMessage

from hallw.core import AgentRunner
from hallw.server.socket_renderer import SocketRenderer


class Session:
    def __init__(
        self,
        sid: str,
        sio: socketio.AsyncServer,
        main_loop: asyncio.AbstractEventLoop,
        session_id: str,
        thread_id: str | None = None,
    ):
        self.session_id = session_id
        self.thread_id = thread_id if thread_id else session_id
        self.renderer = SocketRenderer(sio, sid, main_loop, session_id=session_id)
        self.history: list[BaseMessage] = []
        self.input_tokens = 0
        self.output_tokens = 0
        self.active_runner: AgentRunner | None = None

        # --- Persistent Event Loop & Thread ---
        self.session_loop = asyncio.new_event_loop()
        self.session_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.session_thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.session_loop)
        self.session_loop.run_forever()

    def close(self):
        # Stop the session loop safely
        self.session_loop.call_soon_threadsafe(self.session_loop.stop)
        self.session_thread.join(timeout=2.0)
