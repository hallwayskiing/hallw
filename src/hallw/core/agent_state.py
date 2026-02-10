from typing import Annotated, List, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


def merge_stats(left: Optional[dict], right: Optional[dict]) -> dict:
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
    messages: Annotated[List[BaseMessage], add_messages]
    # Reducer: merge_stats sums up the increments
    stats: Annotated[AgentStats, merge_stats]
    current_stage: int
    total_stages: int
    stage_names: List[str]
    task_completed: bool
