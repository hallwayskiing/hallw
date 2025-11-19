import json
from typing import Any, Dict, Optional


def build_tool_response(success: bool, message: str, data: Optional[Dict[str, Any]] = None) -> str:
    """Serialize tool results into a JSON string with a success flag."""
    payload: Dict[str, Any] = {
        "success": success,
        "message": message,
    }

    if data:
        payload["data"] = data

    return json.dumps(payload, ensure_ascii=False)
