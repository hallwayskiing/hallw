from langchain_core.tools import tool

from hallw.utils import config

from ..utils.tool_response import build_tool_response
from .playwright_mgr import get_page


@tool
async def browser_fill(element_id: str, text: str, submit_on_enter: bool = False) -> str:
    """
    Fill a text input.

    Args:
        element_id: The ID of the element.
        text: The text to fill.
        submit_on_enter: If True, press 'Enter' after filling. Useful for search bars.
    """
    page = await get_page()
    if page is None:
        return build_tool_response(False, "Please launch browser first.")

    # CSS Selector: "id='foo' OR data-hallw-id='foo'"
    selector = f"[id='{element_id}'], [data-hallw-id='{element_id}']"

    try:
        # Verify existence
        if await page.locator(selector).count() == 0:
            return build_tool_response(False, f"Element [{element_id}] not found. ID might be stale.")

        await page.fill(selector, text, timeout=config.pw_click_timeout)

        msg = f"Filled [{element_id}] with '{text}'."

        if submit_on_enter:
            await page.press(selector, "Enter")
            msg += " Pressed Enter."
            # Wait for potential navigation
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=2000)
            except Exception:
                pass

        return build_tool_response(True, msg, {"filled_id": element_id})

    except Exception as e:
        return build_tool_response(False, f"Error: {str(e)}")
