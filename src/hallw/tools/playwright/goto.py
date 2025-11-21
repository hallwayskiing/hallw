from langchain_core.tools import tool
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.tools import build_tool_response

from .playwright_state import GOTO_TIMEOUT, get_page


@tool
async def browser_goto(url: str) -> str:
    """Navigate the page to a URL.

    Args:
        url: Target URL

    Returns:
        Status message
    """
    page = await get_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=GOTO_TIMEOUT)
        return build_tool_response(True, "Navigation successful.", {"url": url})
    except PlaywrightTimeoutError:
        return build_tool_response(
            False,
            f"Timeout while navigating to {url}, \
            maybe the page is not reachable or network conditions are poor.",
        )
