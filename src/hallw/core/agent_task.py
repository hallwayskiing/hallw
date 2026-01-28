import asyncio
from concurrent.futures import CancelledError
from typing import Dict, Optional

from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import BaseCheckpointSaver

from hallw.utils import config

from .agent_event_loop import AgentEventLoop
from .agent_graph import build_graph
from .agent_renderer import AgentRenderer
from .agent_state import AgentState


class AgentTask:
    def __init__(
        self,
        task_id: str,
        llm: ChatOpenAI,
        tools_dict: Dict[str, BaseTool],
        renderer: AgentRenderer,
        initial_state: AgentState,
        checkpointer: BaseCheckpointSaver,
        event_loop: AgentEventLoop,
    ):
        self.task_id = task_id
        self.llm = llm
        self.tools_dict = tools_dict
        self.renderer = renderer
        self.initial_state = initial_state
        self.checkpointer = checkpointer
        self.event_loop = event_loop
        self._future: Optional[asyncio.Future] = None

    def run(self) -> None:
        """
        Synchronous entry point to run the agent task.
        """
        self._future = self.event_loop.submit(self.run_async())
        try:
            self._future.result()
        except CancelledError:
            pass
        finally:
            self._future = None

    def cancel(self) -> None:
        """Request cancellation of the running task."""
        if self._future and not self._future.done():
            self._future.cancel()

    async def run_async(self) -> None:
        workflow = build_graph(self.llm, self.tools_dict, self.checkpointer)
        invocation_config = {
            "recursion_limit": config.model_max_recursion,
            "configurable": {"thread_id": self.task_id},
        }
        event = None

        try:
            async for event in workflow.astream_events(
                self.initial_state,
                config=invocation_config,
                version="v2",
            ):
                self.renderer.handle_event(event)
        except Exception as e:
            if event is None:
                error_name = "unknown"
            else:
                error_name = event["event"]
            self.renderer.handle_event(
                {
                    "event": "on_fatal_error",
                    "run_id": self.task_id,
                    "name": error_name,
                    "data": {"error": str(e)},
                }
            )
