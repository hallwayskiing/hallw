import asyncio
from typing import Dict, Optional

from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import BaseCheckpointSaver

from hallw.utils import config

from .agent_graph import build_graph
from .agent_renderer import AgentRenderer
from .agent_state import AgentState


class AgentTask:
    """
    Represents a single agent task execution.
    Now runs directly in the main event loop without a separate thread.
    """

    def __init__(
        self,
        task_id: str,
        llm: ChatOpenAI,
        tools_dict: Dict[str, BaseTool],
        renderer: AgentRenderer,
        initial_state: AgentState,
        checkpointer: BaseCheckpointSaver,
    ):
        self.task_id = task_id
        self.llm = llm
        self.tools_dict = tools_dict
        self.renderer = renderer
        self.initial_state = initial_state
        self.checkpointer = checkpointer
        self._task: Optional[asyncio.Task] = None

    def start(self) -> asyncio.Task:
        """
        Start the agent task as an asyncio Task in the current event loop.
        Returns the Task object for tracking/cancellation.
        """
        self._task = asyncio.create_task(self._run())
        return self._task

    async def cancel(self) -> None:
        """Request cancellation of the running task."""
        if self._task and not self._task.done():
            self._task.cancel()

    @property
    def is_running(self) -> bool:
        """Check if the task is still running."""
        return self._task is not None and not self._task.done()

    async def _run(self) -> None:
        """Internal async execution of the agent workflow."""
        workflow = build_graph(self.llm, self.tools_dict, self.checkpointer, self.renderer)
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
                kind = event.get("event")
                data = event.get("data", {})
                name = event.get("name", "")
                run_id = event.get("run_id", "")

                if kind == "on_chain_start" and name == "LangGraph":
                    self.renderer.on_task_started()
                elif kind == "on_chain_end" and name == "LangGraph":
                    self.renderer.on_task_finished()
                elif kind == "on_chat_model_start":
                    self.renderer.on_llm_start()
                elif kind == "on_chat_model_stream":
                    chunk = data.get("chunk")
                    if chunk is not None:
                        self.renderer.on_llm_chunk(chunk)
                elif kind == "on_chat_model_end":
                    self.renderer.on_llm_end()
                elif kind == "on_tool_start":
                    self.renderer.on_tool_start(run_id, name, data.get("input"))
                elif kind == "on_tool_end":
                    self.renderer.on_tool_end(run_id, name, data.get("output"))
                elif kind == "on_tool_error":
                    self.renderer.on_tool_error(run_id, name, data.get("error"))
                elif kind == "on_fatal_error":
                    self.renderer.on_fatal_error(run_id, name, data.get("error"))

        except asyncio.CancelledError:
            # Task was cancelled, this is expected behavior
            raise
        except Exception as e:
            error_name = event["event"] if event else "unknown"
            self.renderer.on_fatal_error(self.task_id, error_name, str(e))
