import urllib.parse

from langchain_core.tools import tool

from hallw.tools import build_tool_response
from hallw.utils import config, logger

from .playwright_mgr import get_page


@tool
async def browser_search(page_index: int, query: str) -> str:
    """Search the web for a query and return titles and URLs.

    Args:
        page_index: Index of the page to perform the search on.
        query: Search query keywords

    Returns:
        Formatted string with search results including titles and URLs or error message
    """
    # Get fresh config values
    goto_timeout = config.pw_goto_timeout
    captcha_timeout = config.manual_captcha_timeout
    result_count = config.search_result_count

    # 1. Setup search engine configuration
    search_engine = config.browser_search_engine
    engine = search_engine.lower() if search_engine else "google"
    supported_engines = ["google", "baidu", "bing"]

    if engine not in supported_engines:
        engine = "google"
        logger.warning("Unsupported search engine specified. Defaulting to Google.")

    page = await get_page(page_index)
    if page is None:
        return build_tool_response(False, f"Page with index {page_index} not found.")

    encoded_query = urllib.parse.quote_plus(query)

    # --- Core: Define URL, captcha features, and result extraction rules ---
    engine_rules = {
        "google": {
            "url": f"https://www.google.com/search?q={encoded_query}",
            # Success indicator: search results container appears
            "success_selector": "div#search",
            # Captcha/interception features: presence of these elements indicates blocking
            "captcha_selectors": [
                'iframe[src*="recaptcha"]',
                "#captcha-form",
                "div#recaptcha",
                "div#infoDiv",  # Google "Sorry" page container
            ],
            "result_selector": "div#search a:has(h3)",
            "title_in_child": "h3",
        },
        "baidu": {
            "url": f"https://www.baidu.com/s?wd={encoded_query}",
            "success_selector": "#content_left",
            # Baidu security verification usually has wappass class or verification ID
            "captcha_selectors": [
                ".wappass-content",
                "div#verification",
                "div.c-exception",  # Sometimes network error
                "#se-security-check",
            ],
            "result_selector": "#content_left .c-container h3 a",
            "title_in_child": None,
        },
        "bing": {
            "url": f"https://www.bing.com/search?q={encoded_query}",
            "success_selector": "#b_results",
            "captcha_selectors": ["#challenge-container", "iframe#iframe-challenge", ".b_captcha"],
            "result_selector": "#b_results > li.b_algo h2 a",
            "title_in_child": None,
        },
    }

    rule = engine_rules[engine]

    # 2. Execute navigation
    try:
        await page.goto(rule["url"], wait_until="domcontentloaded", timeout=goto_timeout)
    except Exception:
        return build_tool_response(
            False,
            f"Timeout while requesting {engine}, possibly due to network or severe blocking.",
            {"page_index": page_index},
        )

    # 3. Unified captcha detection logic
    is_captcha_detected = False

    # Iterate over all possible captcha elements defined for the engine
    for cap_selector in rule["captcha_selectors"]:
        try:
            if await page.query_selector(cap_selector):
                is_captcha_detected = True
                break
        except Exception:
            pass  # Ignore minor errors during query

    # 4. If captcha detected, enter long wait mode
    if is_captcha_detected:
        try:
            # Wait for user to manually solve until the "success indicator" appears
            await page.wait_for_selector(rule["success_selector"], timeout=captcha_timeout)
            logger.info(f"User successfully passed {engine} CAPTCHA.")
        except Exception:
            return build_tool_response(
                False,
                f"{engine.capitalize()} CAPTCHA Timeout: Verification was not completed in time.",
                {"page_index": page_index},
            )

    # 5. Regularly wait for results to load
    try:
        await page.wait_for_selector(
            rule["success_selector"], state="attached", timeout=goto_timeout
        )
    except Exception:
        return build_tool_response(
            False,
            f"Failed to load search results on {engine}. \
            Maybe blocked or network issue.",
            {"page_index": page_index},
        )

    # 6. Parse results
    results = []
    link_locators = page.locator(rule["result_selector"])
    count = 0
    total_found = await link_locators.count()

    for i in range(total_found):
        if count >= result_count:
            break

        link_elem = link_locators.nth(i)

        try:
            url = await link_elem.get_attribute("href")
            # Basic filtering: exclude javascript: links and empty links
            if not url or not url.startswith(("http", "https")):
                continue

            title = ""
            if rule["title_in_child"]:
                child = link_elem.locator(rule["title_in_child"])
                if await child.count() > 0:
                    title = await child.inner_text()
            else:
                title = await link_elem.inner_text()

            if title:
                title = title.strip()

            if title and url:
                results.append(f"{count+1}. {title} - {url}")
                count += 1

        except Exception as e:
            logger.debug(f"Error parsing result {i}: {e}")
            continue

    if not results:
        return build_tool_response(False, f"No valid search results found on {engine}.")

    return build_tool_response(
        True,
        f"Top {len(results)} search results from {engine} for '{query}'.",
        {"results": results, "page_index": page_index},
    )
