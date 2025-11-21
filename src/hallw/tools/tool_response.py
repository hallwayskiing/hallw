import json
from typing import Any, Dict, Optional, TypedDict


class ToolResult(TypedDict, total=False):
    """Result structure for tool responses."""

    success: bool
    message: str
    data: Dict[str, Any]


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

    # Build validated result
    result: ToolResult = {
        "success": bool(parsed.get("success", False)),
        "message": str(parsed.get("message", "")),
    }

    # Normalize data field if present
    if "data" in parsed:
        data = parsed["data"]
        if isinstance(data, dict):
            result["data"] = data
        else:
            # Convert non-dict data to dict or ignore
            result["data"] = {"value": data}

    return result
