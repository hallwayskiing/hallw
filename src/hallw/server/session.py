import asyncio

import socketio
from langchain_core.messages import BaseMessage

from hallw.core import AgentRunner
from hallw.server.socket_renderer import SocketRenderer
from hallw.tools.playwright.playwright_mgr import BrowserWorker


class Session:
    """
    Represents a single user chat session.
    """

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

        # asyncio.Task running run_wrapper on the main loop
        self.task: asyncio.Task | None = None

        # Dedicated Playwright thread
        self.browser = BrowserWorker(session_id)

    def close(self) -> None:
        """
        Clean up session resources.
        """
        self.browser.close()
