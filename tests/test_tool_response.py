"""Tests for tool_response module."""

import json

import pytest

from hallw.tools.tool_response import build_tool_response, parse_tool_response


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


def test_parse_tool_response_valid():
    """Test parsing a valid tool response."""
    raw = build_tool_response(True, "Success", {"result": "data"})
    parsed = parse_tool_response(raw)

    assert parsed["success"] is True
    assert parsed["message"] == "Success"
    assert parsed["data"] == {"result": "data"}


def test_parse_tool_response_invalid_json():
    """Test parsing invalid JSON returns error response."""
    parsed = parse_tool_response("not valid json {")

    assert parsed["success"] is False
    assert "Invalid JSON" in parsed["message"]


def test_parse_tool_response_not_dict():
    """Test parsing non-dict JSON returns error response."""
    parsed = parse_tool_response('["list", "not", "dict"]')

    assert parsed["success"] is False
    assert "not a dict" in parsed["message"]


def test_parse_tool_response_missing_fields():
    """Test parsing response with missing fields uses defaults."""
    parsed = parse_tool_response('{"other": "field"}')

    assert parsed["success"] is False  # Default for missing success
    assert parsed["message"] == ""  # Default for missing message


def test_parse_tool_response_non_dict_data():
    """Test parsing response with non-dict data normalizes it."""
    parsed = parse_tool_response('{"success": true, "message": "test", "data": "string_data"}')

    assert parsed["success"] is True
    assert parsed["message"] == "test"
    assert parsed["data"] == {"value": "string_data"}
