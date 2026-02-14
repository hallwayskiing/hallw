from langchain_core.tools import tool

from hallw.tools import build_tool_response


@tool
def end_current_stage(stage_count: int = 1) -> str:
    """
    Call this tool to explicit advance to the next stage or completion.

    Args:
        stage_count: The number of stages to complete. Defaults to 1.
                     If set to 0, stages remain unchanged.
                     If set to -1, it will complete all remaining stages and finish the task.

    Returns:
        A confirmation message.
    """
    if stage_count == -1:
        return build_tool_response(True, "All remaining stages successfully completed.")

    if stage_count == 0:
        return build_tool_response(True, "Stages remain unchanged.")

    if stage_count > 1:
        return build_tool_response(True, f"{stage_count} stages successfully completed.")

    return build_tool_response(
        True,
        "Stage successfully completed.",
    )
