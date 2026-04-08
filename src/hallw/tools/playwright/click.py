from langchain_core.tools import tool
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.utils import config

from ..utils.tool_response import build_tool_response
from .playwright_mgr import get_page


@tool
async def browser_click(element_id: str) -> str:
    """Click an element by ID.

    Args:
        element_id (str): The ID of the element to click.

    Returns:
        The result of the click operation.
    """
    page = await get_page()
    if page is None:
        return build_tool_response(False, "Please launch browser first.")

    # Support both native ID and injected data-hallw-id
    selector = f"[id='{element_id}'], [data-hallw-id='{element_id}']"

    try:
        # 1. Existence check
        loc = page.locator(selector).first
        if await loc.count() == 0:
            return build_tool_response(False, f"Element [{element_id}] not found. The page might have refreshed.")

        # 2. Ensure element is scrolled into view and centered
        await loc.scroll_into_view_if_needed()

        # 3. Progressive Click Strategy
        clicked = False

        # Strategy A: Standard simulated click
        try:
            await loc.click(timeout=config.pw_click_timeout)
            clicked = True
        except PlaywrightTimeoutError:
            pass

        # Strategy B: Force click
        if not clicked:
            try:
                await loc.click(force=True, timeout=config.pw_click_timeout)
                clicked = True
            except Exception:
                pass

        # Strategy C: Native JS click
        if not clicked:
            try:
                await page.evaluate(f'document.querySelector("{selector}").click()')
                clicked = True
            except Exception:
                pass

        if not clicked:
            return build_tool_response(False, f"Failed to click [{element_id}]. Element might be covered or moved.")

        # 4. Wait for page to load
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=2000)
        except Exception:
            pass

        return build_tool_response(
            True, f"Successfully clicked [{element_id}].", {"url": page.url, "title": await page.title()}
        )

    except Exception as e:
        return build_tool_response(False, f"Unexpected click error: {str(e)}")
