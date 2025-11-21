from typing import Annotated, List, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class Stats(TypedDict):
    """Statistics for agent execution."""

    tool_call_counts: int
    failures: int
    input_tokens: int
    output_tokens: int
    reflections: int


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    task_completed: bool
    stats: Stats
