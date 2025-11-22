from langchain_core.tools import tool
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.tools import build_tool_response

from .playwright_state import CLICK_TIMEOUT, get_page


@tool
async def browser_fill(page_index: int, role: str, name: str, text: str) -> str:
    """Fill an input field with text.

    Args:
        page_index: Index of the page to perform the fill on.
        role: ARIA role, e.g., "textbox", "combobox", "searchbox", etc.
        name: Accessibility name of the input field
        text: Text to fill

    Returns:
        Status message
    """
    page = await get_page(page_index)
    if page is None:
        return build_tool_response(False, f"Page with index {page_index} not found.")
    count = await page.get_by_role(role=role, name=name).count()
    if count == 0:
        return build_tool_response(
            False, "No input field found.", {"page_index": page_index, "role": role, "name": name}
        )
    elif count > 1:
        return build_tool_response(
            False,
            f"Multiple ({count}) input fields found.",
            {"page_index": page_index, "role": role, "name": name},
        )

    try:
        await page.get_by_role(role=role, name=name).fill(text, timeout=CLICK_TIMEOUT)
        return build_tool_response(
            True,
            "Input filled successfully.",
            {"page_index": page_index, "role": role, "name": name, "text": text},
        )
    except PlaywrightTimeoutError:
        return build_tool_response(
            False,
            "Timeout while filling, maybe the element is not editable or invisible.",
            {"page_index": page_index, "role": role, "name": name},
        )
