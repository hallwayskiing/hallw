from langchain_core.tools import tool
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.tools import build_tool_response

from .playwright_state import GOTO_TIMEOUT, get_page


@tool
async def browser_goto(page_index: int, url: str) -> str:
    """Navigate the page to a URL.

    Args:
        page_index: Index of the page to perform the navigation on.
        url: Target URL

    Returns:
        Status message
    """
    page = await get_page(page_index)
    if page is None:
        return build_tool_response(False, f"Page with index {page_index} not found.")
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=GOTO_TIMEOUT)
        return build_tool_response(
            True, "Navigated to URL successfully.", {"page_index": page_index, "url": url}
        )
    except PlaywrightTimeoutError:
        return build_tool_response(
            False,
            f"Timeout while navigating to {url}, \
            maybe the page is not reachable or network conditions are poor.",
            {"page_index": page_index, "url": url},
        )
    except Exception as e:
        return build_tool_response(
            False, f"Error while navigating to {url}: {e}", {"page_index": page_index, "url": url}
        )
