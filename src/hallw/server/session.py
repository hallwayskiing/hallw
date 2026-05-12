import asyncio

import socketio
from langchain_core.messages import BaseMessage, HumanMessage

from hallw.core import AgentRunner, AgentState
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
        self.state: AgentState = {
            "messages": [],
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
            "steering_queue": [],
        }
        self.active_runner: AgentRunner | None = None

        # asyncio.Task running run_wrapper on the main loop
        self.task: asyncio.Task | None = None

        # Dedicated Playwright thread
        self.browser = BrowserWorker(session_id)

    @property
    def messages(self) -> list[BaseMessage]:
        return self.state["messages"]

    @property
    def input_tokens(self) -> int:
        return self.state["stats"].get("input_tokens", 0)

    @property
    def output_tokens(self) -> int:
        return self.state["stats"].get("output_tokens", 0)

    @property
    def steering_queue(self) -> list[HumanMessage]:
        return self.state.setdefault("steering_queue", [])

    def enqueue_steering(self, message: HumanMessage) -> None:
        self.steering_queue.append(message)

    def close(self) -> None:
        """
        Clean up session resources.
        """
        self.browser.close()
