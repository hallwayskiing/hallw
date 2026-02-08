import asyncio

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from hallw.tools import build_tool_response


@tool
async def request_user_input(prompt: str, config: RunnableConfig) -> str:
    """
    Pause execution and ask the user for input at runtime. Use this when you need
    clarification, additional information, or user decisions between stages.

    Args:
        prompt: The message to display to the user explaining what input is needed.

    Returns:
        The user's input response as a string.
    """
    renderer = config.get("configurable", {}).get("renderer")

    if renderer is None:
        return build_tool_response(
            success=False,
            message="No renderer available to request user input.",
        )

    try:
        # Request user input through the renderer (timeout: 5 minutes)
        response = await renderer.on_request_user_input(
            prompt=prompt,
            timeout=300,
        )

        if response == "timeout":
            return build_tool_response(
                success=False,
                message="User input request timed out after 5 minutes.",
            )

        if response == "rejected":
            return build_tool_response(
                success=False,
                message="User rejected the input request.",
            )

        return build_tool_response(
            success=True,
            message="User input received successfully.",
            data={"user_input": response},
        )

    except asyncio.CancelledError:
        return build_tool_response(
            success=False,
            message="Input request was cancelled.",
        )
    except Exception as e:
        return build_tool_response(
            success=False,
            message=f"Failed to request user input: {str(e)}",
        )
