from abc import ABC, abstractmethod
from typing import Any


class AgentRenderer(ABC):
    """
    Abstract base class for rendering agent events.
    Responsible for defining the interface and handling common event dispatch logic.
    """

    @abstractmethod
    def on_llm_start(self) -> None:
        """Called when LLM starts generating response."""

    @abstractmethod
    def on_llm_chunk(self, chunk: Any) -> None:
        """Called when a new chunk of LLM response is received."""

    @abstractmethod
    def on_llm_end(self) -> None:
        """Called when LLM finishes generating response."""

    @abstractmethod
    def on_tool_start(self, run_id: str, name: str, args: Any) -> None:
        """Called when a tool execution starts."""

    @abstractmethod
    def on_tool_end(self, run_id: str, name: str, output: Any) -> None:
        """Called when a tool execution completes successfully."""

    @abstractmethod
    def on_tool_error(self, run_id: str, name: str, error: Any) -> None:
        """Called when a tool execution fails."""

    @abstractmethod
    def on_fatal_error(self, run_id: str, name: str, error: Any) -> None:
        """Called when a fatal error occurs in the agent."""

    # --- Domain Specific Events (Migrated from Event Bus) ---

    @abstractmethod
    def on_stage_started(self, data: dict) -> None:
        """Called when a new task stage starts."""

    @abstractmethod
    def on_stage_completed(self, data: dict) -> None:
        """Called when a task stage completes."""

    @abstractmethod
    def on_tool_plan_updated(self, data: dict) -> None:
        """Called when the high-level tool execution plan is updated."""

    @abstractmethod
    async def on_request_confirmation(self, request_id: str, timeout: int, message: str) -> str:
        """Called when agent needs user confirmation."""

    @abstractmethod
    def on_resolve_confirmation(self, request_id: str, status: str) -> None:
        """Called when agent resolves user confirmation."""

    @abstractmethod
    async def on_request_user_input(self, prompt: str, timeout: int) -> str:
        """Called when agent needs arbitrary user input."""

    @abstractmethod
    def on_resolve_user_input(self, request_id: str, status: str, value: str = None) -> None:
        """Called when agent resolves user input request."""
