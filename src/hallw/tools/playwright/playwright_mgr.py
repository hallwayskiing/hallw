"""Playwright browser manager with singleton pattern."""

import socket
import time
from typing import Optional

from langchain_core.tools import ToolException
from playwright.async_api import BrowserContext, Page, Playwright, async_playwright
from playwright_stealth.stealth import Stealth

from hallw.utils import config


class PlaywrightManager:
    """Singleton manager for Playwright browser state and operations."""

    _instance: Optional["PlaywrightManager"] = None

    def __new__(cls) -> "PlaywrightManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize all state variables."""
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        self.pw: Optional[Playwright] = None
        self.main_app_page: Optional[Page] = None
        self.target_view: Optional[Page] = None

    def reset(self) -> None:
        """Reset all state variables to initial values."""
        self.pw = None
        self.main_app_page = None
        self.target_view = None

    # -------------------------
    # Page Management
    # -------------------------

    async def get_page(self) -> Optional[Page]:
        """Get the primary Agent View page."""
        return self.target_view

    # -------------------------
    # Browser Lifecycle
    # -------------------------

    async def launch(self):
        """Connect to the Electron frontend via CDP.

        Returns:
            Status message
        """
        # Get config values
        cdp_port = 9222
        cdp_timeout = config.pw_cdp_timeout
        endpoint = f"http://127.0.0.1:{cdp_port}"

        # Wait for port to be available (Electron CDP initialization might take a moment)
        if not _wait_for_port("127.0.0.1", cdp_port, timeout=cdp_timeout):
            raise ToolException(f"Failed to connect via CDP on port {cdp_port}")

        self.pw = await async_playwright().start()

        try:
            browser = await self.pw.chromium.connect_over_cdp(endpoint)

            # The newly opened blank window will be in the default context
            context = browser.contexts[0] if len(browser.contexts) > 0 else await browser.new_context()

            await _apply_stealth(context)

            # Identify the specific Agent View by checking the injected JS variable
            for page in context.pages:
                try:
                    is_agent_view = await page.evaluate("() => window.__IS_AGENT_VIEW__ === true")
                except Exception:
                    is_agent_view = False

                if page.url.startswith("file://") or "localhost:" in page.url:
                    self.main_app_page = page
                elif is_agent_view:
                    self.target_view = page

        except Exception as e:
            raise ToolException(f"Failed to connect via CDP: {e}")

    async def disconnect(self) -> None:
        """Disconnect from CDP without closing the browser."""
        if self.pw:
            try:
                await self.pw.stop()
            except Exception:
                pass
        self.reset()


# -------------------------
# Helpers
# -------------------------


async def _apply_stealth(context: BrowserContext) -> None:
    """Apply stealth settings to context."""
    stealth = Stealth()
    await stealth.apply_stealth_async(context)


def _wait_for_port(host: str, port: int, timeout: float = 1000) -> bool:
    """Wait for a TCP port to become available."""
    deadline = time.time() + timeout / 1000
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (socket.error, OSError):
            time.sleep(0.2)
    return False


# -------------------------
# Exports
# -------------------------
pw_manager = PlaywrightManager()


async def get_page() -> Optional[Page]:
    """Get the primary page."""
    return await pw_manager.get_page()


async def browser_launch():
    """Launch browser."""
    return await pw_manager.launch()


async def browser_disconnect() -> None:
    """Disconnect CDP connection."""
    await pw_manager.disconnect()
