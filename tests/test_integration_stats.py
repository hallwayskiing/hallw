"""Integration test for agent graph with typed stats and reflection logic."""

import pytest
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from hallw.agent_state import AgentState
from hallw.tools import build_tool_response


@tool
async def test_tool(text: str) -> str:
    """A simple test tool."""
    return build_tool_response(True, "Success", {"text": text})


def test_agent_state_with_stats():
    """Test creating an AgentState with fully typed stats."""
    state: AgentState = {
        "messages": [HumanMessage(content="test")],
        "task_completed": False,
        "stats": {
            "tool_call_counts": 5,
            "failures": 3,
            "input_tokens": 100,
            "output_tokens": 50,
            "reflections": 1,
        },
    }

    # Verify all fields are accessible
    assert state["stats"]["tool_call_counts"] == 5
    assert state["stats"]["failures"] == 3
    assert state["stats"]["input_tokens"] == 100
    assert state["stats"]["output_tokens"] == 50
    assert state["stats"]["reflections"] == 1
    assert state["task_completed"] is False


def test_stats_updates():
    """Test that stats can be updated."""
    state: AgentState = {
        "messages": [],
        "task_completed": False,
        "stats": {
            "tool_call_counts": 0,
            "failures": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "reflections": 0,
        },
    }

    # Simulate some operations
    state["stats"]["tool_call_counts"] += 1
    state["stats"]["failures"] += 1
    state["stats"]["input_tokens"] += 50
    state["stats"]["output_tokens"] += 25

    assert state["stats"]["tool_call_counts"] == 1
    assert state["stats"]["failures"] == 1
    assert state["stats"]["input_tokens"] == 50
    assert state["stats"]["output_tokens"] == 25
