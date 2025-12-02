import re

from langchain_core.tools import tool
from markdownify import markdownify as md

from hallw.tools import build_tool_response
from hallw.utils import config

from .helpers import auto_consent, remove_overlays
from .playwright_mgr import get_page


@tool
async def browser_get_content(page_index: int, segment: int) -> str:
    """Fetch the main content of the page as Markdown, returned in segments.

    Converts HTML to Markdown to preserve structure (headers, lists, links)
    while removing noise (scripts, styles, images).

    Args:
        page_index: Index of the page to fetch content from.
        segment: Segment index (0-based)

    Returns:
        Markdown content of the page by segment.
    """
    page = await get_page(page_index)
    if page is None:
        return build_tool_response(False, f"Page with index {page_index} not found.")

    try:
        await page.wait_for_load_state("load", timeout=3000)
        await remove_overlays(page)
        await auto_consent(page)
    except Exception:
        pass

    # 2. Auto select content container
    selectors = [
        "article",
        "[role='main']",
        "main",
        ".post-content",
        ".article-body",
        "#content",
        "#main",
        ".main-content",
        ".entry-content",
        "body",  # Fallback
    ]

    html_content = ""
    found_selector = ""

    # 3. Get HTML from the first matching selector
    for selector in selectors:
        element = page.locator(selector)
        count = await element.count()
        if count > 0:
            # Get the HTML content of the first matching element
            html_content = await element.nth(0).inner_html()
            found_selector = selector
            break

    if not html_content.strip():
        return build_tool_response(False, "The page content is empty or could not be detected.")

    # 4. Convert HTML to Markdown using Markdownify
    try:
        markdown_content = md(
            html_content,
            heading_style="ATX",
            strip=["script", "style", "img", "svg", "iframe", "noscript", "form", "nav", "footer"],
        )
    except Exception as e:
        # If conversion fails, fallback to plain text
        return build_tool_response(False, f"Error converting content to markdown: {str(e)}")

    # 5. Post-processing: Clean up excessive blank lines and whitespace
    cleaned_content = re.sub(r"\n{3,}", "\n\n", markdown_content)
    cleaned_content = cleaned_content.strip()

    if not cleaned_content:
        return build_tool_response(False, "Content became empty after cleaning noise.")

    # 6. Segment the content
    max_chars = config.max_page_content_chars
    segment = max(segment, 0)
    total_len = len(cleaned_content)
    segments = (total_len + max_chars - 1) // max_chars
    offset = max_chars * segment

    if segment >= segments:
        return build_tool_response(
            False,
            f"Segment index {segment} out of range. Total segments: {segments}.",
            {"page_index": page_index, "total_segments": segments},
        )

    segment_text = cleaned_content[offset : offset + max_chars]

    return build_tool_response(
        True,
        f"Fetched markdown content (Segment {segment+1}/{segments}). Source: {found_selector}",
        {
            "page_index": page_index,
            "segment": segment,
            "total_segments": segments,
            "chars_per_segment": max_chars,
            "content": segment_text,
        },
    )
