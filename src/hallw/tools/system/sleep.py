import asyncio

from langchain_core.tools import tool

from hallw.tools import build_tool_response


@tool
async def sleep(seconds: int) -> str:
    """
    Pause execution for a specified number of seconds.
    Use this to simulate delays or control the pace of execution.

    Args:
        seconds (int): The number of seconds to sleep. Range: 1 to 10.

    Returns:
        A message indicating that the sleep operation was completed.
    """
    if not (1 <= seconds <= 10):
        return build_tool_response(False, "Seconds must be between 1 and 10.")

    await asyncio.sleep(seconds)
    return build_tool_response(
        success=True,
        message=f"Slept for {seconds} seconds.",
    )
