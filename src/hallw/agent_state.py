from typing import Annotated, List, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentStats(TypedDict):
    tool_call_counts: int
    input_tokens: int
    output_tokens: int
    failures: int
    failures_since_last_reflection: int


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    task_completed: bool
    stats: AgentStats
