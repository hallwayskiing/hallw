from langchain_core.tools import tool

from hallw.tools import build_tool_response

from .playwright_state import add_page


@tool
async def browser_open_new_page() -> str:
    """Open a new browser page.
    You control 1 page at start. This tool opens an additional page.

    Returns:
        Index of the new page or error message.
    """
    try:
        index = await add_page()
        return build_tool_response(True, "New page opened successfully.", {"page_index": index})
    except Exception as e:
        return build_tool_response(False, f"Failed to open new page: {e}")
