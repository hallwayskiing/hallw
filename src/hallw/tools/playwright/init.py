from langchain_core.tools import tool

from hallw.tools import build_tool_response

from .playwright_mgr import browser_launch


@tool
async def browser_init(headless: bool = True) -> str:
    """Initialize the browser. Call this tool before using any other browser tools.

    Args:
        headless: Whether to run the browser in headless mode.
        Default to True. Set to False if user's task requires visual interaction.

    Returns:
        str: Status message.
    """
    try:
        await browser_launch(headless)
        return build_tool_response(True, "Browser initialized successfully")
    except Exception as e:
        return build_tool_response(False, f"Browser initialization failed: {str(e)}")
