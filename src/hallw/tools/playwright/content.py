import trafilatura
from langchain_core.tools import tool
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.utils import config

from ..utils.tool_response import build_tool_response
from .helpers import auto_consent, remove_overlays
from .playwright_mgr import get_page


@tool
async def browser_get_content() -> str:
    """Get content from a page.

    Returns:
        Status message with the final page title, url and content in markdown format.
    """
    max_content_length = config.pw_content_max_length

    page = await get_page()
    if page is None:
        return build_tool_response(False, "Please launch browser first.")

    try:
        await page.wait_for_load_state("domcontentloaded", timeout=5000)

        try:
            await page.wait_for_load_state("networkidle", timeout=3000)
        except PlaywrightTimeoutError:
            pass

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

        if len(extracted_text) > max_content_length:
            extracted_text = extracted_text[:max_content_length] + "...(truncated)"

        return build_tool_response(
            True,
            f"Successfully get content from {url}",
            {
                "title": page_title,
                "url": url,
                "content": extracted_text,
            },
        )

    except PlaywrightTimeoutError:
        return build_tool_response(
            False,
            f"Timeout while getting content from {url}. Site might be slow or blocking bot traffic.",
        )
    except Exception as e:
        return build_tool_response(False, f"Error while getting content from {url}: {str(e)}")
