from langchain_core.tools import tool

from ..utils.tool_response import build_tool_response
from .helpers import auto_consent, remove_overlays
from .playwright_mgr import get_page

# JavaScript for robustly extracting page structure
SCRIPT = """
() => {
    const idAttribute = 'data-hallw-id';
    const allowedTags = ['button', 'a', 'input', 'select', 'textarea', 'details', 'summary'];
    const allowedRoles = ['button', 'link', 'checkbox', 'combobox', 'option', 'tab',
    'searchbox', 'textbox', 'menuitem', 'menu', 'radio', 'switch'];

    function isEffectivelyVisible(el) {
        // 1. Size check
        const rect = el.getBoundingClientRect();
        if (rect.width <= 4 || rect.height <= 4) return false;

        // 2. Style check
        const style = window.getComputedStyle(el);
        if (style.visibility === 'hidden' || style.display === 'none' || parseFloat(style.opacity) === 0) return false;

        // 3. Hidden attribute check
        if (el.hidden) return false;

        // 4. ARIA hidden check
        if (el.getAttribute('aria-hidden') === 'true') return false;

        // 5. Out of viewport check
        const isOutOfViewport = rect.bottom < 0 || rect.top > window.innerHeight;
        if (isOutOfViewport) return false;

        return true;
    }

    const items = [];
    let idCounter = 1;

    function scan(node) {
        if (!node) return;

        // Traverse ShadowRoot/DocumentFragment containers
        if (!node.tagName) {
            const containerChildren = Array.from(node.children || []);
            for (const child of containerChildren) {
                scan(child);
            }
            return;
        }

        const tagName = node.tagName.toLowerCase();
        const role = node.getAttribute('role');

        // 1. Check interactivity based on tag, role, attributes, and styles
        let isInteractive = allowedTags.includes(tagName) || allowedRoles.includes(role);
        if (!isInteractive) {
            const classAttr = node.getAttribute('class') || '';
            const style = window.getComputedStyle(node);
            if (node.onclick ||
                node.getAttribute('jsaction') ||
                node.getAttribute('data-action') ||
                (typeof classAttr === 'string' && classAttr.includes('btn')) ||
                style.cursor === 'pointer') {
                isInteractive = true;
            }
        }
        // 2. If interactive and visible, extract name and assign ID
        if (isInteractive && isEffectivelyVisible(node)) {
            let name = node.getAttribute('aria-label') || node.innerText || node.getAttribute('title') ||
                        node.getAttribute('placeholder') || "";
            if (tagName === 'img' && !name) {
                name = node.getAttribute('alt') || "Image";
            }
            name = name.replace(/\s+/g, ' ').trim().slice(0, 100);
            const isInput = ['input', 'select', 'textarea', 'textbox', 'searchbox'].includes(tagName) ||
                            ['textbox', 'searchbox'].includes(role);
            // Only include elements that have a name or are input-like (even if unnamed)
            if (name || isInput) {
                let aid = node.getAttribute(idAttribute);
                if (!aid) {
                    const nativeId = node.id;
                    if (nativeId && nativeId.length < 50 && !/\\d{10,}/.test(nativeId)) {
                        aid = nativeId;
                    } else {
                        aid = String(idCounter++);
                        node.setAttribute(idAttribute, aid);
                    }
                }

                items.push({
                    id: aid,
                    role: role || tagName,
                    name: name
                });
            }
        }

        // 3. Recursively scan Shadow DOM and children
        if (node.shadowRoot) {
            scan(node.shadowRoot);
        }
        const children = Array.from(node.children || []);
        for (const child of children) {
            scan(child);
        }
    }

    scan(document.body || document.documentElement);

    return {
        elements: items
    };
}
"""


@tool
async def browser_get_structure() -> str:
    """Get interactive elements on the page.

    Returns:
        The url, title and a list of interactive elements of the page.
    """

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
        prefix = "input" if el["role"] in ["input", "textarea", "textbox", "searchbox"] else el["role"]
        entry = {
            "id": el["id"],
            "role": prefix,
            "name": el["name"],
        }
        formatted_elements.append(entry)

    return build_tool_response(
        True,
        f"Fetched structure with {len(formatted_elements)} interactive elements.",
        {
            "url": page.url,
            "title": await page.title(),
            "elements": formatted_elements,
        },
    )
