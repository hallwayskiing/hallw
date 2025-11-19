from langchain_core.tools import tool
from playwright.async_api import TimeoutError as PlayWrightTimeoutError

from hallw.tools import build_tool_response

from .playwright_state import get_page


@tool
async def browser_get_structure() -> str:
    """
    Get the page structure, focusing on:
    1. Page Title and URL.
    2. Key "interactive" elements (buttons, links, inputs, comboboxes, etc.).

    Returns:
        A structured string representation of the page.
    """
    page = await get_page()

    # -------------------------
    # A11y Tree Extraction
    # -------------------------
    snapshot = await page.accessibility.snapshot()
    a11y_items = []

    # Whitelist of high-value interactive roles for the agent
    ALLOWED_ROLES = {
        "button",
        "link",
        "combobox",  # Dropdown select
        "searchbox",  # Search input
        "textbox",  # Text input
        "option",  # Option in a select
        "tab",  # Tab in a tab list
    }

    def walk(node):
        if not node:
            return

        role = node.get("role")
        name = node.get("name")

        # Core optimization: Only include nodes that are in the whitelist
        # and have a non-empty name.
        if role in ALLOWED_ROLES and name:
            a11y_items.append((role, name))

        for c in node.get("children", []):
            walk(c)

    if snapshot:
        walk(snapshot)

    # Deduplicate and limit to prevent context overflow
    a11y_items = list(dict.fromkeys(a11y_items))
    a11y_items = await _filter_visible_role_entries(page, a11y_items)

    interactive_data = []
    for idx, (role, name) in enumerate(a11y_items, 1):
        label = name or ""
        interactive_data.append(
            {
                "index": idx,
                "role": role,
                "name": label,
            }
        )

    return build_tool_response(
        True,
        "Fetched page structure.",
        {
            "title": await page.title(),
            "url": page.url,
            "interactive_elements": interactive_data,
        },
    )


async def _filter_visible_role_entries(page, role_name_pairs):
    """Ensure reported accessibility nodes have at least one visible DOM match."""
    visible_items = []

    for role, name in role_name_pairs:
        locator = page.get_by_role(role, name=name, exact=True)
        try:
            match_count = await locator.count()
        except PlayWrightTimeoutError:
            continue

        for idx in range(match_count):
            handle = locator.nth(idx)
            try:
                if await handle.is_visible(timeout=250):
                    visible_items.append((role, name))
                    break
            except PlayWrightTimeoutError:
                continue

    return visible_items
