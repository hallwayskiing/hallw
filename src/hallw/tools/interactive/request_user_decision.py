from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from hallw.tools import build_tool_response


@tool
async def request_user_decision(prompt: str, options: list[str] = None, config: RunnableConfig = None) -> str:
    """
    Pause execution and ask the user for a decision or input at runtime.
    Use this when you need clarification, additional information, or user decisions between stages.

    Args:
        prompt: The message to display to the user explaining what input is needed.
        options: A list of options for the user to choose from. If None, the user can input free text.

    Returns:
        The user's input response as a string.
    """
    renderer = config.get("configurable", {}).get("renderer")

    if renderer is None:
        return build_tool_response(
            success=False,
            message="No renderer available to request user decision.",
        )

    try:
        # Request user input through the renderer (timeout: 5 minutes)
        response = await renderer.on_request_user_decision(
            prompt=prompt,
            options=options,
            timeout=300,
        )

        if response == "timeout":
            return build_tool_response(
                success=False,
                message="User decision request timed out after 5 minutes.",
            )

        if response == "rejected":
            return build_tool_response(
                success=False,
                message="User rejected the decision request.",
            )

        return build_tool_response(
            success=True,
            message="User decision received successfully.",
            data={"user_input": response},
        )

    except Exception as e:
        return build_tool_response(
            success=False,
            message=f"Failed to request user decision: {str(e)}",
        )
