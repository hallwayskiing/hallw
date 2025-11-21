"""Tests for agent_state module."""

from langchain_core.messages import HumanMessage

from hallw.agent_state import AgentState, Stats


def test_stats_typed_dict():
    """Test Stats TypedDict structure."""
    stats: Stats = {
        "tool_call_counts": 5,
        "failures": 2,
        "input_tokens": 100,
        "output_tokens": 50,
        "reflections": 0,
    }

    assert stats["tool_call_counts"] == 5
    assert stats["failures"] == 2
    assert stats["input_tokens"] == 100
    assert stats["output_tokens"] == 50
    assert stats["reflections"] == 0


def test_agent_state_structure():
    """Test AgentState TypedDict structure."""
    state: AgentState = {
        "messages": [HumanMessage(content="test")],
        "task_completed": False,
        "stats": {
            "tool_call_counts": 0,
            "failures": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "reflections": 0,
        },
    }

    assert len(state["messages"]) == 1
    assert state["task_completed"] is False
    assert state["stats"]["tool_call_counts"] == 0
