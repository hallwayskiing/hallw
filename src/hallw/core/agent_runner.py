import asyncio
from typing import Self

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_litellm import ChatLiteLLM
from langgraph.checkpoint.base import BaseCheckpointSaver

from hallw.utils import config

from .agent_event_dispatcher import AgentEventDispatcher
from .agent_graph import build_graph
from .agent_renderer import AgentRenderer
from .agent_state import AgentState


class AgentRunner:
    """
    Represents a single agent task execution.
    Runs inside a Session-specific Event Loop on a background thread.
    """

    def __init__(
        self,
        task_id: str,
        llm: BaseChatModel,
        dispatcher: AgentEventDispatcher,
        initial_state: AgentState,
        checkpointer: BaseCheckpointSaver,
        invocation_config: RunnableConfig,
    ):
        self.task_id = task_id
        self.task: asyncio.Task | None = None
        self.llm = llm
        self.dispatcher = dispatcher
        self.initial_state = initial_state
        self.checkpointer = checkpointer
        self.invocation_config = invocation_config

    @property
    def is_running(self) -> bool:
        """Check if the task is still running."""
        return self.task is not None and not self.task.done()

    def cancel(self) -> None:
        """Request cancellation of the running task thread-safely."""
        if self.task and not self.task.done():
            try:
                loop = self.task.get_loop()
                loop.call_soon_threadsafe(self.task.cancel)
            except AttributeError:
                # Fallback for older asyncio or custom loops
                self.task.cancel()

    async def run(self) -> AgentState | None:
        """Internal async execution of the agent workflow. Returns the final agent state."""
        workflow = build_graph(self.llm, self.checkpointer)
        event = None

        try:
            async for event in workflow.astream_events(
                self.initial_state,
                config=self.invocation_config,
                version="v2",
            ):
                # Delegate event handling to the dispatcher
                await self.dispatcher.dispatch(event)

            # Get the final state after stream processing is complete
            final_state: AgentState = (await workflow.aget_state(self.invocation_config)).values
            return final_state

        except asyncio.CancelledError:
            # Task was cancelled, this is expected behavior
            raise
        except Exception as e:
            # Safely get event type if available
            error_type = "unknown"
            if event and isinstance(event, dict):
                error_type = event.get("event", "unknown")

            await self.dispatcher.dispatch(
                {"event": "on_fatal_error", "run_id": self.task_id, "name": error_type, "data": {"error": str(e)}}
            )
            # Try to get final state even if error
            try:
                except_state: AgentState = (await workflow.aget_state(self.invocation_config)).values
                return except_state
            except Exception:
                return None

    @classmethod
    def create(
        cls,
        messages: list[BaseMessage],
        thread_id: str,
        renderer: AgentRenderer,
        checkpointer: BaseCheckpointSaver,
    ) -> Self:
        """Factory method to create and initialize a new AgentRunner instance."""
        # LLM Configuration
        llm = ChatLiteLLM(
            model=config.model_name,
            temperature=config.model_temperature,
            max_tokens=config.model_max_output_tokens,
            streaming=True,
            stream_usage=True,
            stream_options={"include_usage": True},
            model_kwargs={
                "reasoning_effort": config.model_reasoning_effort,
            },
        )

        # Build initial state
        initial_state: AgentState = {
            "messages": messages,
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
        }

        invocation_config: RunnableConfig = {
            "recursion_limit": config.model_max_recursion,
            "configurable": {
                "thread_id": thread_id,
                "renderer": renderer,
            },
        }

        return cls(
            task_id=thread_id,
            llm=llm,
            dispatcher=AgentEventDispatcher(renderer),
            initial_state=initial_state,
            checkpointer=checkpointer,
            invocation_config=invocation_config,
        )
