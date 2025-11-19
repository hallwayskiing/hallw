from langchain_core.tools import tool
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.tools import build_tool_response

from .playwright_state import CLICK_TIMEOUT, get_page


@tool
async def browser_fill(role: str, name: str, text: str) -> str:
    """Fill an input field with text.

    Args:
        role: ARIA role, e.g., "textbox", "combobox", "searchbox", etc.
        name: Accessibility name of the input field
        text: Text to fill

    Returns:
        Status message
    """
    page = await get_page()
    count = await page.get_by_role(role=role, name=name).count()
    if count == 0:
        return build_tool_response(
            False, f"No input field found with role '{role}' and name '{name}'"
        )
    elif count > 1:
        return build_tool_response(
            False, f"Multiple ({count}) input fields found with role '{role}' and name '{name}'"
        )

    try:
        await page.get_by_role(role=role, name=name).fill(text, timeout=CLICK_TIMEOUT)
        return build_tool_response(
            True, "Input filled successfully.", {"role": role, "name": name, "text": text}
        )
    except PlaywrightTimeoutError:
        return build_tool_response(
            False,
            f"Timeout while filling '{name}', maybe the element is not editable or invisible.",
        )
