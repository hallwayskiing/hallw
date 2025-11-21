"""Tests for reflection and failure counting logic."""

from hallw.agent_state import AgentState


def test_reflection_trigger_logic():
    """Test the reflection trigger logic based on failures and reflections."""
    # Helper to test the logic from route_from_tools
    def should_trigger_reflection(failures: int, reflections: int) -> bool:
        """Reproduce the logic from route_from_tools."""
        if failures > 0 and failures % 3 == 0:
            expected_reflections = failures // 3
            if reflections < expected_reflections:
                return True
        return False

    # No failures - no reflection
    assert should_trigger_reflection(0, 0) is False

    # 1-2 failures - no reflection
    assert should_trigger_reflection(1, 0) is False
    assert should_trigger_reflection(2, 0) is False

    # 3 failures - first reflection
    assert should_trigger_reflection(3, 0) is True

    # After first reflection, 3 failures should not trigger again
    assert should_trigger_reflection(3, 1) is False

    # 4-5 failures - no new reflection
    assert should_trigger_reflection(4, 1) is False
    assert should_trigger_reflection(5, 1) is False

    # 6 failures - second reflection
    assert should_trigger_reflection(6, 1) is True

    # After second reflection
    assert should_trigger_reflection(6, 2) is False

    # 7-8 failures - no new reflection
    assert should_trigger_reflection(7, 2) is False
    assert should_trigger_reflection(8, 2) is False

    # 9 failures - third reflection
    assert should_trigger_reflection(9, 2) is True


def test_reflection_count_increments():
    """Test that reflections count is properly incremented."""
    state: AgentState = {
        "messages": [],
        "task_completed": False,
        "stats": {
            "tool_call_counts": 0,
            "failures": 3,
            "input_tokens": 0,
            "output_tokens": 0,
            "reflections": 0,
        },
    }

    stats = state["stats"]

    # Simulate the route_from_tools logic
    if stats["failures"] > 0 and stats["failures"] % 3 == 0:
        expected_reflections = stats["failures"] // 3
        if stats["reflections"] < expected_reflections:
            stats["reflections"] += 1

    # After 3 failures, reflections should be 1
    assert stats["reflections"] == 1

    # Next time with same failure count, should not increment
    if stats["failures"] > 0 and stats["failures"] % 3 == 0:
        expected_reflections = stats["failures"] // 3
        if stats["reflections"] < expected_reflections:
            stats["reflections"] += 1

    assert stats["reflections"] == 1  # Still 1

    # After 6 failures
    stats["failures"] = 6
    if stats["failures"] > 0 and stats["failures"] % 3 == 0:
        expected_reflections = stats["failures"] // 3
        if stats["reflections"] < expected_reflections:
            stats["reflections"] += 1

    assert stats["reflections"] == 2

