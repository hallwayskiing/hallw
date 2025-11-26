"""Tests for tool_response module."""

import json

from hallw.tools.tool_response import build_tool_response, parse_tool_response


def test_build_tool_response_success_with_data():
    payload = build_tool_response(True, "Operation successful", {"key": "value", "count": 42})
    data = json.loads(payload)

    assert data == {
        "success": True,
        "message": "Operation successful",
        "data": {"key": "value", "count": 42},
    }


def test_build_tool_response_omits_none_data():
    payload = build_tool_response(True, "Test", None)
    data = json.loads(payload)

    assert data == {"success": True, "message": "Test"}


def test_parse_tool_response_validates_types():
    parsed = parse_tool_response('{"success": "true", "message": "ok", "data": {"a":1}}')
    assert parsed["success"] is True
    assert parsed["message"] == "ok"
    assert parsed["data"] == {"a": 1}


def test_parse_tool_response_handles_invalid_json():
    parsed = parse_tool_response("not-json")
    assert parsed["success"] is False
    assert "Invalid JSON" in parsed["message"]


def test_parse_tool_response_normalizes_data():
    parsed = parse_tool_response('{"success": false, "message": "m", "data": 3}')
    assert parsed["success"] is False
    assert parsed["data"] == {"value": 3}
