import trafilatura
from langchain_core.tools import tool
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.tools import build_tool_response

from .helpers import auto_consent, remove_overlays
from .playwright_mgr import get_page


@tool
async def browser_get_content(page_index: int) -> str:
    """Get content from a page.
    Args:
        page_index: Index of the page to get content from.

    Returns:
        Status message with the final page title, url and content in markdown format.
    """
    page = await get_page(page_index)
    if page is None:
        return build_tool_response(False, "Launch browser first or page index is invalid.")

    try:
        await page.wait_for_load_state("networkidle", timeout=10000)

        try:
            await auto_consent(page)
            await remove_overlays(page)
        except Exception:
            pass

        html = await page.content()
        page_title = await page.title()
        url = page.url

        extracted_text = trafilatura.extract(
            html,
            output_format="markdown",
            include_links=True,
            include_comments=False,
            deduplicate=True,
        )

        if not extracted_text:
            return build_tool_response(False, f"Could not extract meaningful content from {url}")

        if len(extracted_text) > 10000:
            extracted_text = extracted_text[:10000] + "...(Truncated)"

        return build_tool_response(
            True,
            f"Successfully get content from page {page_index}",
            {
                "title": page_title,
                "url": url,
                "content": extracted_text,
            },
        )

    except PlaywrightTimeoutError:
        return build_tool_response(
            False,
            f"Timeout while getting content from page {page_index}. Site might be slow or blocking bot traffic.",
        )
    except Exception as e:
        return build_tool_response(False, f"Error while getting content from page {page_index}: {str(e)}")
