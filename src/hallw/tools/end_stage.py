from langchain_core.tools import tool

from hallw.tools import build_tool_response


@tool
def end_current_stage() -> str:
    """
    Call this tool to explicitly proceed to the next stage or completion.

    Args:
        None

    Returns:
        A confirmation message.
    """
    return build_tool_response(
        True,
        "Stage successfully completed.",
    )
