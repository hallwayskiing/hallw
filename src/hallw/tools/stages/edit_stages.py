from langchain_core.tools import tool

from ..utils.tool_response import build_tool_response


@tool
def edit_stages(new_stages: list[str]) -> str:
    """
    Replace all remaining (uncompleted) stages with a brand-new list.

    Use this tool when your current plan needs adjustment — for example, when
    a stage turns out to be unnecessary, or you discover additional work that
    was not in the original plan.

    Args:
        new_stages (list[str]): A list of new stage names to replace the remaining stages.

    Returns:
        A confirmation message.
    """
    if not new_stages:
        return build_tool_response(False, "new_stages cannot be empty.")
    return build_tool_response(True, "Stages updated successfully.", {"new_stages": new_stages})
