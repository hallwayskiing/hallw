from langchain_core.tools import tool

from ..utils.tool_response import build_tool_response


@tool
def build_stages(stage_names: list[str]) -> str:
    """
    Analyze the task and provide a list of stages with their corresponding names.

    Args:
        stage_names (list[str]): A list of stage names.
    Returns:
        A formatted string listing the stages.
    """

    return build_tool_response(
        True,
        "Stages built successfully.",
        {
            "stage_names": stage_names,
        },
    )
