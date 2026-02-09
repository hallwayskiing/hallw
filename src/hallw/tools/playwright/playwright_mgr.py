"""Playwright browser manager with singleton pattern."""

import os
import shutil
import socket
import subprocess
import tempfile
import time
from typing import Optional

from langchain_core.tools import ToolException
from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright
from playwright_stealth.stealth import Stealth

from hallw.utils import config, logger


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
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.chrome_process: Optional[subprocess.Popen] = None
        self.temp_user_data_dir: Optional[str] = None

    def reset(self) -> None:
        """Reset all state variables to initial values."""
        self.pw = None
        self.browser = None
        self.context = None
        self.chrome_process = None
        self.temp_user_data_dir = None

    # -------------------------
    # Page Management
    # -------------------------

    async def get_page(self, index: int) -> Optional[Page]:
        """Get page by index, auto-launching browser if needed."""
        if self.context is None:
            return None

        pages = self.context.pages
        if index >= len(pages):
            return None
        return pages[index]

    async def add_page(self) -> int:
        """Add a new page and return its index."""
        if self.context is None:
            return -1

        await self.context.new_page()
        return len(self.context.pages) - 1

    # -------------------------
    # Browser Lifecycle
    # -------------------------

    async def launch(self, headless: bool = True) -> str:
        """Open Chrome or reuse an existing instance and connect via CDP.

        Returns:
            Status message
        """
        # Get config values
        cdp_port = config.cdp_port
        cdp_timeout = config.pw_cdp_timeout
        prefer_local = config.prefer_local_chrome
        endpoint = f"http://127.0.0.1:{cdp_port}"

        # Check if Chrome is already running
        chrome_already_running = False
        try:
            chrome_already_running = _wait_for_port("127.0.0.1", cdp_port, timeout=cdp_timeout)
        except Exception:
            chrome_already_running = False

        self.pw = await async_playwright().start()

        # 1. Connect to existing Chrome instance
        if chrome_already_running:
            try:
                browser = await self.pw.chromium.connect_over_cdp(endpoint)
                self.browser = browser
                # Create a new context
                self.context = await browser.new_context()
                await self._apply_stealth(self.context)
                await self.context.new_page()
                self.chrome_process = None  # Since we didn't start it

                return "Connected to existing Chrome instance."

            except Exception as e:
                raise ToolException(f"Failed to connect to existing Chrome via CDP: {e}")

        # 2. Launch new Chrome instance
        chrome_path = _find_chrome_executable()
        # If local browser not preferred or not found, use Playwright Chromium
        if not prefer_local or chrome_path is None:
            try:
                args = self._build_chrome_args(headless=headless)
                browser = await self.pw.chromium.launch(args=args, headless=headless)
                self.browser = browser
                context = await browser.new_context()
                await self._apply_stealth(context)
                self.context = context
                await context.new_page()
            except Exception:
                self._cleanup_chrome_process()
                raise ToolException("Playwright Chromium not installed, run `playwright install chromium` first")
            self.chrome_process = None  # It's managed by Playwright
            return "Playwright Chromium launched"
        # Launch local Chrome with CDP
        else:
            args = self._build_chrome_args(chrome_path, headless)

            process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.chrome_process = process

            if not _wait_for_port("127.0.0.1", cdp_port, cdp_timeout):
                self._cleanup_chrome_process()
                raise ToolException("Local Chrome failed to start with CDP.")

            endpoint = f"http://127.0.0.1:{cdp_port}"
            self.browser = await self.pw.chromium.connect_over_cdp(endpoint)
            # Use default context which already contains a page
            self.context = self.browser.contexts[0]
            await self._apply_stealth(self.context)

            return "Local Chrome with CDP started."

    async def close(self) -> None:
        """Close current context/pages."""
        if config.keep_browser_open:
            logger.info("KEEP_PAGE_OPEN is enabled; leaving page open.")
            self.reset()
            return

        if self.context is None:
            logger.info("Browser is not launched.")
            return

        # Close all pages
        for page in self.context.pages:
            try:
                await page.close()
            except Exception:
                continue

        # Close context and browser
        try:
            await self.context.close()
            if self.browser and len(self.browser.contexts) == 0:
                await self.browser.close()
                self._cleanup_chrome_process()
        except Exception:
            pass

        # Stop playwright
        if self.pw is not None:
            try:
                await self.pw.stop()
            except Exception:
                pass

        # Reset state
        self.reset()

        logger.info("Browser successfully closed")

    # -------------------------
    # Internal Helpers
    # -------------------------

    async def _apply_stealth(self, context: BrowserContext) -> None:
        """Apply stealth settings to context."""
        stealth = Stealth()
        await stealth.apply_stealth_async(context)

    def _build_chrome_args(self, chrome_path: str = None, headless: bool = True) -> list:
        """Build Chrome command-line arguments."""
        chrome_user_data_dir = config.chrome_user_data_dir
        cdp_port = config.cdp_port

        if chrome_user_data_dir:
            user_data_dir = os.path.abspath(chrome_user_data_dir)
        else:
            user_data_dir = tempfile.mkdtemp()
            self.temp_user_data_dir = user_data_dir

        if chrome_path:
            args = [
                chrome_path,
                f"--remote-debugging-port={cdp_port}",
                f"--user-data-dir={user_data_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                "--exclude-switches=enable-automation",
                "--disable-dev-shm-usage",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-default-apps",
                "--disable-infobars",
                "--disable-popup-blocking",
                "--disable-notifications",
            ]
            if headless:
                args.append("--headless=new")
        else:
            args = [
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-dev-shm-usage",
                "--disable-default-apps",
                "--disable-infobars",
                "--disable-popup-blocking",
                "--disable-notifications",
            ]
        return args

    def _cleanup_chrome_process(self) -> None:
        """Terminate Chrome process and clean up temporary directory."""
        if self.chrome_process:
            try:
                self.chrome_process.terminate()
                self.chrome_process.wait(timeout=5)
            except Exception:
                try:
                    self.chrome_process.kill()
                except Exception:
                    pass
            self.chrome_process = None

        if self.temp_user_data_dir and os.path.exists(self.temp_user_data_dir):
            shutil.rmtree(self.temp_user_data_dir, ignore_errors=True)
            self.temp_user_data_dir = None


# -------------------------
# Module-level utilities
# -------------------------


def _find_chrome_executable() -> Optional[str]:
    """Find Chrome executable across different platforms."""
    possible_paths = [
        os.environ.get("CHROME_PATH"),
        shutil.which("chrome"),
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/chrome",
        "/usr/bin/chromium",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for path in possible_paths:
        if path and os.path.exists(path):
            return path
    return None


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


async def get_page(index: int) -> Optional[Page]:
    """Get page by index."""
    return await pw_manager.get_page(index)


async def add_page() -> int:
    """Add a new page and return its index."""
    return await pw_manager.add_page()


async def browser_launch(headless: bool = True) -> str:
    """Launch browser."""
    return await pw_manager.launch(headless)


async def browser_close() -> None:
    """Close browser."""
    await pw_manager.close()
