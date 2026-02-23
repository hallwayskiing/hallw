from langchain_core.tools import tool

from ..utils.tool_response import build_tool_response


@tool
def dummy_for_missed_tool(name: str) -> str:
    """
    A dummy tool function that returns a "Tool Not Found" response.

    Args:
        name (str): The name of the missing tool.

    Returns:
        str: A standardized tool response indicating the tool was not found.
    """
    return build_tool_response(success=False, message=f"Tool {name} Not Found")
