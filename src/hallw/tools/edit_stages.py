from typing import List

from langchain_core.tools import tool

from hallw.tools import build_tool_response


@tool
def edit_stages(new_stages: List[str]) -> str:
    """
    Replace all remaining (uncompleted) stages with a brand-new list.

    Use this tool when your current plan needs adjustment — for example, when
    a stage turns out to be unnecessary, or you discover additional work that
    was not in the original plan.

    The stages you provide will **completely replace** every stage that has
    not yet been completed.  Already-completed stages are preserved.

    Args:
        new_stages: A non-empty list of new stage names that will replace the
                    remaining stages.

    Returns:
        A confirmation message.
    """
    if not new_stages:
        return build_tool_response(False, "new_stages cannot be empty.")
    return build_tool_response(True, "Stages updated successfully.", {"new_stages": new_stages})
