"""Tests for finish_task tool."""

import json

from hallw.tools.finish_task import finish_task


def test_finish_task_success():
    """Test finishing a task successfully."""
    reason = "All steps completed successfully"
    result = finish_task.invoke({"reason": reason})
    data = json.loads(result)

    assert data["success"] is True
    assert data["message"] == "Task completed successfully."
    assert data["data"]["reason"] == reason


def test_finish_task_with_detailed_reason():
    """Test finishing a task with detailed reason."""
    reason = "User requested task is done. All files saved and browser closed."
    result = finish_task.invoke({"reason": reason})
    data = json.loads(result)

    assert data["success"] is True
    assert data["data"]["reason"] == reason
