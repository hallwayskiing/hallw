import asyncio

from playwright.async_api import Page


async def remove_overlays(page: Page):
    """
    Helper: Inject JS to aggressively remove common modal overlays,
    cookie banners, and restore scrolling.
    """
    js_script = """
    () => {
        // 1. Common selectors for annoying overlays
        const selectors = [
            '#onetrust-banner-sdk', '.onetrust-banner', // OneTrust
            '.fc-consent-root', // Funding Choices
            'div[class*="cookie"]', 'div[id*="cookie"]',
            'div[class*="modal"]', 'div[id*="modal"]',
            'div[class*="popup"]', 'div[id*="popup"]',
            'div[class*="overlay"]', 'div[id*="overlay"]',
            '[aria-modal="true"]',
            '.ub-emb-iframe-wrapper',
            '.adsbox',
            '#credential_picker_container', // Google Sign-in prompt
            'iframe[title*="consent"]'
        ];

        // 2. Remove elements
        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => {
                // Safety check: ensure we don't delete the main body or extremely large wrappers
                // unless they are fixed/absolute positioned (typical for overlays)
                const style = window.getComputedStyle(el);
                if (style.position === 'fixed' || style.position === 'absolute' || parseInt(style.zIndex) > 50) {
                    el.remove();
                }
            });
        });

        // 3. Force enable scrolling (many modals set overflow: hidden on body)
        document.body.style.overflow = 'auto';
        document.body.style.position = 'static';
        document.documentElement.style.overflow = 'auto';
    }
    """
    try:
        await page.evaluate(js_script)
    except Exception:
        pass  # Fail silently, don't block main logic


async def auto_consent(page: Page):
    """
    Helper: Attempt to click 'Agree/Accept' buttons for cookies or age verification.
    """
    # Common keywords for positive action
    keywords = [
        "Accept All",
        "I Accept",
        "Agree",
        "I Agree",
        "Allow",
        "Allow all",
        "Yes, I am 18",
        "Enter Site",
        "Got it",
        "Understand",
    ]

    # Try to find and click
    for word in keywords:
        try:
            # Look for button-like elements or links containing the keyword
            # 'exact=False' allows fuzzy matching (e.g. "Accept Cookies")
            locator = page.get_by_text(word, exact=False)

            # Check if visible before clicking to avoid errors
            if await locator.count() > 0:
                first_match = locator.first
                if await first_match.is_visible():
                    await first_match.click(timeout=1000, no_wait_after=True)
                    # Small wait for animation/reload
                    await asyncio.sleep(0.5)
                    break  # Stop after first successful click
        except Exception:
            continue
