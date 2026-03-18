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
        try:
            self.session_loop.run_forever()
        finally:
            pending = asyncio.all_tasks(self.session_loop)
            for task in pending:
                task.cancel()

            if pending:
                self.session_loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

            # Run a brief sleep to allow deferred cancellations and callbacks (like aiohttp teardown) to schedule
            self.session_loop.run_until_complete(asyncio.sleep(0.1))

            # Second pass: gather any new cleanup tasks spawned during the flush
            pending = asyncio.all_tasks(self.session_loop)
            if pending:
                self.session_loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

            if hasattr(self.session_loop, "shutdown_asyncgens"):
                self.session_loop.run_until_complete(self.session_loop.shutdown_asyncgens())

            if hasattr(self.session_loop, "shutdown_default_executor"):
                try:
                    self.session_loop.run_until_complete(self.session_loop.shutdown_default_executor())
                except Exception:
                    pass

            self.session_loop.close()

    def close(self):
        # Stop the session loop safely
        if self.session_loop.is_running():
            self.session_loop.call_soon_threadsafe(self.session_loop.stop)

        if self.session_thread.is_alive():
            self.session_thread.join(timeout=5.0)
