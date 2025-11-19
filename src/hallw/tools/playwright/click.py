from langchain_core.tools import tool
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.tools import build_tool_response

from .playwright_state import CLICK_TIMEOUT, get_page


@tool
async def browser_click(
    role: str = None,
    name: str = None,
) -> str:
    """
    Click an element by accessible role and name.

    Args:
        role: ARIA role, e.g., "button", "link", "textbox"
        name: Accessible name of the element

    Returns:
        Status message
    """
    page = await get_page()
    count = await page.get_by_role(role, name=name).count()
    if count == 0:
        return build_tool_response(False, f"No '{role}' found with name='{name}'")
    try:
        await page.get_by_role(role, name=name).first.click(timeout=CLICK_TIMEOUT)
        return build_tool_response(
            True, "Element clicked successfully.", {"role": role, "name": name}
        )
    except PlaywrightTimeoutError:
        return build_tool_response(
            False,
            f"Timeout while clicking '{role}', maybe the element is not clickable or invisible.",
        )
