from typing import List

from langchain_core.tools import tool

from hallw.tools import build_tool_response


@tool
def build_stages(stage_names: List[str]) -> str:
    """
    Analyze the task and provide a list of stages with their corresponding names.

    Args:
        stage_names: A list of stage names.
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
