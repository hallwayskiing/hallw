from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


def merge_stats(left: dict | None, right: dict | None) -> dict:
    """Automatically sums up token counts and tool metrics."""
    if left is None:
        left = {}
    if right is None:
        return left

    new_stats = left.copy()
    for k, v in right.items():
        new_stats[k] = left.get(k, 0) + v
    return new_stats


class AgentStats(TypedDict):
    input_tokens: int
    output_tokens: int
    tool_call_counts: int
    failures: int
    failures_since_last_reflection: int


class AgentState(TypedDict):
    # Reducer: add_messages appends new messages to the list
    messages: Annotated[list[BaseMessage], add_messages]
    # Reducer: merge_stats sums up the increments
    stats: Annotated[AgentStats, merge_stats]
    current_stage: int
    total_stages: int
    stage_names: list[str]
    task_completed: bool


def create_agent_state(messages: list[BaseMessage]) -> AgentState:
    """Build a fresh AgentState for a new graph invocation."""
    return {
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
