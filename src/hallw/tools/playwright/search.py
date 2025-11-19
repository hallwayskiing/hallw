from langchain_core.tools import tool

from hallw.tools import build_tool_response
from hallw.utils import logger

from .playwright_state import GOTO_TIMEOUT, MANUAL_CAPTCHA_TIMEOUT, SEARCH_RESULT_COUNT, get_page


@tool
async def browser_search(query: str) -> str:
    """Search Google for a query and return titles and URLs of top results

    Args:
        query: Search query keywords

    Returns:
        Formatted string with search results including titles and URLs or error message
    """
    page = await get_page()
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    try:
        await page.goto(search_url, wait_until="domcontentloaded", timeout=GOTO_TIMEOUT)
    except Exception:
        return build_tool_response(
            False, "Timeout while searching, maybe network conditions are poor."
        )

    # Detect CAPTCHA
    if await page.query_selector('iframe[src*="recaptcha"]') or await page.query_selector(
        "#captcha-form"
    ):
        logger.warning("Google reCAPTCHA detected, please complete the verification in browser")
        try:
            await page.wait_for_selector("div#search", timeout=MANUAL_CAPTCHA_TIMEOUT)
        except Exception:
            return build_tool_response(
                False, "reCAPTCHA Timeout: unable to retrieve search results."
            )

    await page.wait_for_selector("div#search", timeout=GOTO_TIMEOUT)
    results = []
    search_container = page.locator("div#search")
    link_locators = search_container.locator("a:has(h3)")
    count = 0

    for i in range(await link_locators.count()):
        if count >= SEARCH_RESULT_COUNT:
            break
        link_elem = link_locators.nth(i)
        title_elem = link_elem.locator("h3")
        try:
            if await title_elem.count() > 0:
                title = await title_elem.inner_text()
                url = await link_elem.get_attribute("href")
            else:
                continue
            if title and url and url.startswith("http"):
                results.append(f"{count+1}. {title} - {url}")
                count += 1
        except Exception:
            continue

    if not results:
        if await link_locators.count() > 0 and count == 0:
            return build_tool_response(
                False,
                "Found potential result links, but all were filtered out (e.g., non-http URLs).",
            )
        return build_tool_response(False, "No valid search results found.")

    return build_tool_response(True, f"Search results for '{query}'.", {"results": results})
