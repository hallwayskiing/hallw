from langchain_core.tools import tool

from hallw.tools import build_tool_response

from .helpers import auto_consent, remove_overlays
from .playwright_mgr import get_page

# JavaScript for robustly extracting page structure
# Focuses on interactive and visible elements, using a hybrid ID strategy
SCRIPT = """
() => {
    const items = [];
    const idAttribute = 'data-hallw-id';

    // Whitelist of interactive tags and roles
    const allowedTags = ['button', 'a', 'input', 'select', 'textarea', 'details', 'summary'];
    const allowedRoles = ['button', 'link', 'checkbox', 'combobox', 'option',
                            'tab', 'searchbox', 'textbox', 'menuitem', 'menu', 'radio', 'switch'];

    // Core visibility check (CSS level)
    function isEffectivelyVisible(el) {
        const rect = el.getBoundingClientRect();
        // 1. Size check
        if (rect.width <= 0 || rect.height <= 0) return false;

        // 2. CSS style check
        const style = window.getComputedStyle(el);
        if (style.visibility === 'hidden' ||
            style.display === 'none' ||
            parseFloat(style.opacity) === 0) {
            return false;
        }

        // 3. HTML attribute check
        if (el.hidden) return false;

        return true;
    }

    const allElements = document.querySelectorAll('*');
    let idCounter = 1;

    for (const el of allElements) {
        const tagName = el.tagName.toLowerCase();
        const role = el.getAttribute('role');

        // --- Filtering logic ---
        let isInteractive = allowedTags.includes(tagName) || allowedRoles.includes(role);

        // Additional capture: div/span disguised as buttons (common in React/Vue)
        if (!isInteractive) {
            const classAttr = el.getAttribute('class') || '';

            // Additional click detection
            if (el.onclick ||
                el.getAttribute('jsaction') ||
                el.getAttribute('data-action') ||
                (typeof classAttr === 'string' && classAttr.includes('btn'))) {
                    isInteractive = true;
            }
        }

        if (!isInteractive) continue;
        if (!isEffectivelyVisible(el)) continue;

        // --- Text extraction ---
        // Priority order: Aria-label > InnerText > Title > Placeholder
        let name = el.getAttribute('aria-label') || el.innerText ||
        el.getAttribute('title') || el.getAttribute('placeholder') || "";

        // Special handling for images
        if (tagName === 'img' && !name) {
            name = el.getAttribute('alt') || "Image";
        }

        // Clean text: compress consecutive spaces
        name = name.replace(/\\s+/g, ' ').trim().slice(0, 100);

        // Inputs are kept even if they have no name
        const isInput = ['input', 'select', 'textarea', 'textbox', 'searchbox'].includes(tagName) ||
        ['textbox', 'searchbox'].includes(role);
        if (!name && !isInput) continue;

        // --- Hybrid ID strategy ---
        let aid = el.getAttribute(idAttribute);
        if (!aid) {
            const nativeId = el.id;
            // Conditions for using native ID: exists + not too long + not likely random
            if (nativeId && nativeId.length < 50 && !/\\d{10,}/.test(nativeId)) {
                aid = nativeId;
            } else {
                // Inject generated ID
                aid = String(idCounter++);
                el.setAttribute(idAttribute, aid);
            }
        }

        items.push({
            id: aid,
            role: role || tagName,
            name: name
        });
    }

    return {
        title: document.title,
        url: window.location.href,
        elements: items
    };
}
"""


@tool
async def browser_get_structure() -> str:
    """Get the robust structure of the page (Viewport independent)."""
    page = await get_page()
    if page is None:
        return build_tool_response(False, "Please launch browser first.")

    # 1. Preprocess: Wait for load, remove overlays, handle consent
    try:
        await page.wait_for_load_state("load", timeout=3000)
        await remove_overlays(page)
        await auto_consent(page)
        await page.wait_for_timeout(500)
    except Exception:
        pass

    try:
        data = await page.evaluate(SCRIPT)
    except Exception as e:
        return build_tool_response(False, f"Structure extraction failed: {str(e)}")

    formatted_elements = []
    for el in data["elements"]:
        # Format output: [ID] Role: Name
        prefix = "Input" if el["role"] in ["input", "textarea", "textbox", "searchbox"] else el["role"].capitalize()
        display = f"[{el['id']}] {prefix}: {el['name']}"
        formatted_elements.append(display)

    return build_tool_response(
        True,
        f"Fetched structure with {len(formatted_elements)} interactive elements.",
        {
            "summary": "\n".join(formatted_elements),
            "url": data["url"],
            "title": data["title"],
        },
    )
