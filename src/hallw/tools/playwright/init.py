from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from hallw.utils import config as app_config

from ..utils.tool_response import build_tool_response
from .playwright_mgr import browser_launch


@tool
async def browser_init(headless: bool = False, config: RunnableConfig = None) -> str:
    """Initialize the browser. Call this tool before using any other browser tools.

    Args:
        headless (bool): Whether to run the browser in headless mode.
        Default to False. Set to True if user's task does not require visual interaction.

    Returns:
        Status message.
    """
    try:
        if config and "configurable" in config and "renderer" in config["configurable"]:
            renderer = config["configurable"]["renderer"]
            status = await renderer.on_request_cdp_page(
                timeout=30, headless=headless, user_data_dir=app_config.chrome_user_data_dir
            )
            if status != "success":
                return build_tool_response(False, f"Frontend failed to open CDP page: {status}.")
        else:
            return build_tool_response(False, "Renderer not found in config.")

        await browser_launch()
        return build_tool_response(True, "Connected to Electron Chrome instance via CDP.")
    except Exception as e:
        return build_tool_response(False, f"Browser initialization failed: {str(e)}.")
