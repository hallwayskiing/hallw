"""Tests for tool_response module."""

import json

from hallw.tools.tool_response import build_tool_response


def test_build_tool_response_success_with_data():
    """Test building a successful tool response with data."""
    result = build_tool_response(True, "Operation successful", {"key": "value", "count": 42})
    data = json.loads(result)

    assert data["success"] is True
    assert data["message"] == "Operation successful"
    assert data["data"] == {"key": "value", "count": 42}


def test_build_tool_response_success_without_data():
    """Test building a successful tool response without data."""
    result = build_tool_response(True, "Operation successful")
    data = json.loads(result)

    assert data["success"] is True
    assert data["message"] == "Operation successful"
    assert "data" not in data


def test_build_tool_response_failure():
    """Test building a failed tool response."""
    result = build_tool_response(False, "Operation failed", {"error": "test error"})
    data = json.loads(result)

    assert data["success"] is False
    assert data["message"] == "Operation failed"
    assert data["data"] == {"error": "test error"}


def test_build_tool_response_with_none_data():
    """Test building a tool response with None data (should not include data field)."""
    result = build_tool_response(True, "Test", None)
    data = json.loads(result)

    assert data["success"] is True
    assert data["message"] == "Test"
    assert "data" not in data


def test_build_tool_response_unicode():
    """Test building a tool response with unicode characters."""
    result = build_tool_response(True, "测试消息", {"中文": "值"})
    data = json.loads(result)

    assert data["success"] is True
    assert data["message"] == "测试消息"
    assert data["data"]["中文"] == "值"
