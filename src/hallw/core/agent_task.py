import logging
from typing import Dict

from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import BaseCheckpointSaver

from .agent_event_loop import AgentEventLoop
from .agent_graph import build_graph
from .agent_renderer import AgentRenderer
from .agent_state import AgentState

logger = logging.getLogger("hallw")


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

    def run(self) -> None:
        """
        Synchronous entry point to run the agent task.
        """
        self.event_loop.submit(self.run_async())

    async def run_async(self) -> None:
        workflow = build_graph(self.llm, self.tools_dict, self.checkpointer)

        invocation_config = {"recursion_limit": 200, "configurable": {"thread_id": self.task_id}}

        try:
            async for event in workflow.astream_events(
                self.initial_state,
                config=invocation_config,
                version="v2",
            ):
                self.renderer.handle_event(event)
        except Exception as e:
            logger.error(f"Error during event {event['event']}: {e}")
            self.renderer.handle_event(
                {
                    "event": "on_fatal_error",
                    "run_id": self.task_id,
                    "name": event["event"],
                    "data": {"error": str(e)},
                }
            )
