from langchain_core.tools import tool

from hallw.tools import build_tool_response


@tool
def finish_task(reason: str) -> str:
    """
    Call this tool when you are 100% certain the task is successfully completed to end the loop.
    This must be your final action. No further steps are needed. No early termination.

    Args:
        reason(str): The reason why you are certain the task is 100% done.
    """
    return build_tool_response(True, "Task completed successfully.", {"reason": reason})
