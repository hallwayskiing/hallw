from langchain_core.tools import tool
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.tools import build_tool_response
from hallw.utils import config

from .playwright_mgr import get_page


@tool
async def browser_click(
    page_index: int,
    role: str = None,
    name: str = None,
) -> str:
    """
    Click an element by accessible role and name.

    Args:
        page_index: Index of the page to perform the click on.
        role: ARIA role, e.g., "button", "link", "textbox".
        name: Accessible name of the element.

    Returns:
        Status message
    """
    page = await get_page(page_index)
    if page is None:
        return build_tool_response(False, f"Page with index {page_index} not found.")
    count = await page.get_by_role(role, name=name).count()
    if count == 0:
        return build_tool_response(False, f"No '{role}' found with name='{name}'")
    try:
        await page.get_by_role(role, name=name).first.click(timeout=config.pw_click_timeout)
        return build_tool_response(
            True,
            "Element clicked successfully.",
            {"page_index": page_index, "role": role, "name": name},
        )
    except PlaywrightTimeoutError:
        return build_tool_response(
            False,
            "Timeout while clicking, maybe the element is not clickable or invisible.",
            {"page_index": page_index, "role": role, "name": name},
        )
