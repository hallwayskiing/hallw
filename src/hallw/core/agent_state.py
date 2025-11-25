from typing import Annotated, List, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentStats(TypedDict, total=False):
    tool_call_counts: int
    input_tokens: int
    output_tokens: int
    failures: int
    failures_since_last_reflection: int


def merge_agent_stats(a: AgentStats, b: AgentStats) -> AgentStats:
    if not a:
        a = {}
    if not b:
        return a
    return {
        "tool_call_counts": a.get("tool_call_counts", 0) + b.get("tool_call_counts", 0),
        "input_tokens": a.get("input_tokens", 0) + b.get("input_tokens", 0),
        "output_tokens": a.get("output_tokens", 0) + b.get("output_tokens", 0),
        "failures": a.get("failures", 0) + b.get("failures", 0),
        "failures_since_last_reflection": a.get("failures_since_last_reflection", 0)
        + b.get("failures_since_last_reflection", 0),
    }


class AgentState(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], add_messages]
    task_completed: bool
    empty_response: bool
    stats: Annotated[AgentStats, merge_agent_stats]
