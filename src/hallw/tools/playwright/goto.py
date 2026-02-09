from langchain_core.tools import tool
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.tools import build_tool_response
from hallw.utils import config

from .helpers import auto_consent, remove_overlays
from .playwright_mgr import get_page


@tool
async def browser_goto(page_index: int, url: str) -> str:
    """Navigate the page to a URL.
    Args:
        page_index: Index of the page to perform the navigation on.
        url: Target URL

    Returns:
        Status message with the final page title.
    """
    page = await get_page(page_index)
    if page is None:
        return build_tool_response(False, "Launch browser first or page index is invalid.")

    try:
        # 1. Basic Navigation
        await page.goto(url, wait_until="domcontentloaded", timeout=config.pw_goto_timeout)

        # 2. Anti-Nuisance Measures
        # We run these concurrently or sequentially.
        # Usually Consent First (polite), then Remove Overlays (aggressive).
        try:
            # Wait a split second for JS-based popups to trigger
            await page.wait_for_timeout(1000)

            await auto_consent(page)
            await remove_overlays(page)
        except Exception:
            # Log warning but don't fail the navigation
            pass

        # 3. Return Success with Context
        final_title = await page.title()
        return build_tool_response(
            True, f"Navigated to {url} successfully.", {"page_index": page_index, "url": page.url, "title": final_title}
        )

    except PlaywrightTimeoutError:
        return build_tool_response(
            False,
            f"Timeout while navigating to {url}. Site might be slow or blocking bot traffic.",
            {"page_index": page_index, "url": url},
        )
    except Exception as e:
        return build_tool_response(
            False, f"Error while navigating to {url}: {str(e)}", {"page_index": page_index, "url": url}
        )
