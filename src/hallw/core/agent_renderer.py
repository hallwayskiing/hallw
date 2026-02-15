from abc import ABC, abstractmethod
from typing import Any


class AgentRenderer(ABC):
    """
    Abstract base class for rendering agent events.
    Responsible for defining the interface and handling common event dispatch logic.
    """

    @abstractmethod
    def on_task_started(self) -> None:
        """Called when a task starts."""

    @abstractmethod
    def on_task_finished(self) -> None:
        """Called when a task finishes."""

    @abstractmethod
    def on_llm_start(self) -> None:
        """Called when LLM starts generating response."""

    @abstractmethod
    def on_llm_chunk(self, text: str, reasoning: str) -> None:
        """Called when a new chunk of LLM response is received."""

    @abstractmethod
    def on_llm_end(self) -> None:
        """Called when LLM finishes generating response."""

    @abstractmethod
    def on_tool_start(self, run_id: str, name: str, args: Any) -> None:
        """Called when a tool execution starts."""

    @abstractmethod
    def on_tool_end(self, run_id: str, name: str, output: Any, is_success: bool, log_msg: str) -> None:
        """Called when a tool execution completes successfully."""

    @abstractmethod
    def on_tool_error(self, run_id: str, name: str, error: Any) -> None:
        """Called when a tool execution fails."""

    @abstractmethod
    def on_fatal_error(self, run_id: str, name: str, error: Any) -> None:
        """Called when a fatal error occurs in the agent."""

    # --- Domain Specific Events ---

    @abstractmethod
    def on_stages_built(self, data: dict) -> None:
        """Called when task stages are built."""

    @abstractmethod
    def on_stage_started(self, data: dict) -> None:
        """Called when a new task stage starts."""

    @abstractmethod
    def on_stages_completed(self, data: dict) -> None:
        """Called when task stages complete."""

    @abstractmethod
    def on_stages_edited(self, data: dict) -> None:
        """Called when remaining stages are replaced with a new plan."""

    @abstractmethod
    async def on_request_confirmation(self, request_id: str, timeout: int, message: str) -> str:
        """Called when agent needs user confirmation."""

    @abstractmethod
    def on_resolve_confirmation(self, request_id: str, status: str) -> None:
        """Called when agent resolves user confirmation."""

    @abstractmethod
    async def on_request_user_decision(self, prompt: str, options: list[str] = None, timeout: int = 300) -> str:
        """Called when agent needs arbitrary user input or decision."""

    @abstractmethod
    def on_resolve_user_decision(self, request_id: str, status: str, value: str = None) -> None:
        """Called when agent resolves user input/decision request."""
