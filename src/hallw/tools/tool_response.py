from __future__ import annotations

import json
from typing import Any, Dict, NotRequired, Optional, TypedDict


class ToolResult(TypedDict):
    """Result structure for tool responses."""

    success: bool
    message: str
    data: NotRequired[Dict[str, Any]]


def build_tool_response(success: bool, message: str, data: Optional[Dict[str, Any]] = None) -> str:
    """Serialize tool results into a JSON string with a success flag."""
    payload: Dict[str, Any] = {
        "success": success,
        "message": message,
    }

    if data:
        payload["data"] = data

    return json.dumps(payload, ensure_ascii=False)


def parse_tool_response(raw_response: str) -> ToolResult:
    """Parse and validate a tool response string.
    Args:
        raw_response: Raw JSON string from tool execution
    Returns:
        Validated ToolResult dict with success, message, and optional data fields
    """
    try:
        parsed = json.loads(raw_response)
    except (json.JSONDecodeError, ValueError) as e:
        return {
            "success": False,
            "message": f"Invalid JSON tool response: {e}",
        }

    if not isinstance(parsed, dict):
        return {
            "success": False,
            "message": f"Tool response is not a dict: {type(parsed).__name__}",
        }

    # Safe parsing of success field
    raw_success = parsed.get("success", False)
    if isinstance(raw_success, str):
        is_success = raw_success.lower() == "true"
    else:
        is_success = bool(raw_success)

    message = str(parsed.get("message", ""))

    result: ToolResult = {"success": is_success, "message": message, "data": None}

    # Normalize data field if present
    if "data" in parsed:
        data = parsed["data"]
        if isinstance(data, dict):
            result["data"] = data
        else:
            # Convert non-dict data to dict or ignore
            result["data"] = {"value": data}

    return result
