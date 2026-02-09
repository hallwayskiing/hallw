from langchain_core.tools import tool
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.tools import build_tool_response
from hallw.utils import config

from .playwright_mgr import get_page


@tool
async def browser_click(page_index: int, element_id: str) -> str:
    """Click an element by ID.

    Args:
        page_index: The index of the page to click on.
        element_id: The ID of the element to click.

    Returns:
        str: The result of the click operation.
    """
    page = await get_page(page_index)
    if page is None:
        return build_tool_response(False, "Launch browser first or page index is invalid.")

    selector = f"[id='{element_id}'], [data-hallw-id='{element_id}']"

    try:
        # 1. Check existence
        loc = page.locator(selector).first
        if await loc.count() == 0:
            return build_tool_response(False, f"Element [{element_id}] not found. The page might have refreshed.")

        # 2. Click
        await loc.click(timeout=config.pw_click_timeout)

        # 3. Wait for result
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=2000)
        except Exception:
            pass

        return build_tool_response(True, f"Clicked [{element_id}]. Page: {await page.title()}", {"url": page.url})

    except PlaywrightTimeoutError:
        return build_tool_response(
            False, f"Timeout clicking [{element_id}]. Element might be covered or non-interactive."
        )
    except Exception as e:
        return build_tool_response(False, f"Click error: {str(e)}")
