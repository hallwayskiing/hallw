from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from hallw.tools import build_tool_response
from hallw.utils import config as app_config


@tool
async def request_user_decision(prompt: str, choices: list[str] | str = None, config: RunnableConfig = None) -> str:
    """
    Pause execution and ask the user for a decision or input at runtime.
    Use this when you need clarification, additional information, or user decisions between stages.
    User can choose from options or input free text.

    Args:
        prompt (str): The message to display to the user explaining what input is needed.
        choices (list[str]): A list of choices for the user to choose from.

    Returns:
        The user's input response as a string.
    """
    request_decision_timeout = app_config.request_decision_timeout

    renderer = config.get("configurable", {}).get("renderer")

    if renderer is None:
        return build_tool_response(
            success=False,
            message="No renderer available to request user decision.",
        )

    # Defensive parsing: if model returns a stringified list, attempt to parse it back into a Python list
    if isinstance(choices, str):
        import ast
        import json

        try:
            # 1. Try standard JSON parsing for '["A", "B"]'
            choices = json.loads(choices)
        except json.JSONDecodeError:
            try:
                # 2. Try Python literal eval for "['A', 'B']" (single quotes)
                choices = ast.literal_eval(str(choices))
            except Exception:
                pass

    if choices is not None and not isinstance(choices, list):
        choices = [str(choices)]

    try:
        # Request user input through the renderer
        response = await renderer.on_request_user_decision(
            prompt=prompt,
            choices=choices,
            timeout=request_decision_timeout,
        )

        if response == "timeout":
            return build_tool_response(
                success=False,
                message=f"User decision request timed out after {request_decision_timeout} seconds.",
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
