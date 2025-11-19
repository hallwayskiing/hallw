from langchain_core.tools import tool

from hallw.tools import build_tool_response

from .playwright_state import MAX_PAGE_CONTENT_CHARS, get_page


@tool
async def browser_get_content(segment: int) -> str:
    """Fetch the text content of the main area of current page by segments.

    Args:
        segment: Segment index (0-based)

    Returns:
        text content of the page by segment
    """
    page = await get_page()

    selectors = [
        "article",
        "[role='main']",
        "main",
        ".post-content",
        ".article-body",
        ".content",
        "#content",
        ".main-content",
        "#main-content",
        ".entry-content",
        ".page-content",
        "body",
    ]

    for selector in selectors:
        element = page.locator(selector)
        count = await element.count()
        if count > 0:
            content = await element.nth(0).inner_text()
            break

    if not content.strip():
        return build_tool_response(False, "The page is empty.")

    segment = max(segment, 0)
    segments = (len(content) + MAX_PAGE_CONTENT_CHARS - 1) // MAX_PAGE_CONTENT_CHARS
    offset = MAX_PAGE_CONTENT_CHARS * segment

    return build_tool_response(
        True,
        "Fetched page content segment.",
        {
            "segment": segment,
            "total_segments": segments,
            "chars_per_segment": MAX_PAGE_CONTENT_CHARS,
            "content": content[offset : offset + MAX_PAGE_CONTENT_CHARS],
        },
    )
