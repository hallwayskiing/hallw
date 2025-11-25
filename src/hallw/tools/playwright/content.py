from langchain_core.tools import tool

from hallw.tools import build_tool_response
from hallw.utils import config

from .playwright_mgr import get_page


@tool
async def browser_get_content(page_index: int, segment: int) -> str:
    """Fetch the text content of the main area of current page by segments.

    Args:
        page_index: Index of the page to fetch content from.
        segment: Segment index (0-based)

    Returns:
        text content of the page by segment
    """
    page = await get_page(page_index)
    if page is None:
        return build_tool_response(False, f"Page with index {page_index} not found.")
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

    max_chars = config.max_page_content_chars
    segment = max(segment, 0)
    segments = (len(content) + max_chars - 1) // max_chars
    offset = max_chars * segment

    if segment >= segments:
        return build_tool_response(
            False,
            f"Segment index {segment} out of range.",
            {"page_index": page_index, "total_segments": segments},
        )

    return build_tool_response(
        True,
        "Fetched page content segment.",
        {
            "page_index": page_index,
            "segment": segment,
            "total_segments": segments,
            "chars_per_segment": max_chars,
            "content": content[offset : offset + max_chars],
        },
    )
