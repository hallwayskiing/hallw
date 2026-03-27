"""Playwright browser manager — per-session, thread-isolated via BrowserWorker."""

import asyncio
import socket
import threading
import time
from contextvars import ContextVar, Token
from typing import Any, Coroutine, TypeVar

from langchain_core.tools import ToolException
from playwright.async_api import BrowserContext, Page, Playwright, async_playwright
from playwright_stealth.stealth import Stealth

from hallw.utils import config

T = TypeVar("T")


# ──────────────────────────────────────────────────────────────────────────────
# Internal Playwright state — lives exclusively on the BrowserWorker thread
# ──────────────────────────────────────────────────────────────────────────────


class _PlaywrightState:
    """Holds Playwright handles. Must only be accessed from its owning BrowserWorker thread."""

    def __init__(self) -> None:
        self.pw: Playwright | None = None
        self.main_app_page: Page | None = None
        self.target_view: Page | None = None

    def reset(self) -> None:
        self.pw = None
        self.main_app_page = None
        self.target_view = None

    async def get_page(self) -> Page | None:
        return self.target_view

    async def launch(self, cdp_port: int = 9222, cdp_timeout: float = 1000) -> None:
        endpoint = f"http://127.0.0.1:{cdp_port}"
        if not _wait_for_port("127.0.0.1", cdp_port, timeout=cdp_timeout):
            raise ToolException(f"Failed to connect via CDP on port {cdp_port}")

        self.pw = await async_playwright().start()
        try:
            browser = await self.pw.chromium.connect_over_cdp(endpoint)
            context = browser.contexts[0] if browser.contexts else await browser.new_context()
            await _apply_stealth(context)

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
        if self.pw:
            try:
                await self.pw.stop()
            except Exception:
                pass
        self.reset()


# ──────────────────────────────────────────────────────────────────────────────
# BrowserWorker — one per Session, runs Playwright on a dedicated thread
# ──────────────────────────────────────────────────────────────────────────────


class BrowserWorker:
    """
    Dedicated thread + event loop for Playwright operations.
    """

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self._state = _PlaywrightState()
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_loop,
            name=f"browser-{session_id[:8]}",
            daemon=True,
        )
        self._thread.start()

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def run(self, coro: Coroutine[Any, Any, T]) -> "asyncio.Future[T]":
        """
        Schedule *coro* on the browser thread's event loop.
        """
        concurrent_future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return asyncio.wrap_future(concurrent_future)

    async def get_page(self) -> Page | None:
        return await self.run(self._state.get_page())

    async def launch(self) -> None:
        await self.run(
            self._state.launch(
                cdp_port=9222,
                cdp_timeout=config.pw_cdp_timeout,
            )
        )

    async def disconnect(self) -> None:
        try:
            await asyncio.wait_for(self.run(self._state.disconnect()), timeout=5.0)
        except Exception:
            pass

    def close(self) -> None:
        """
        Synchronously shut down the browser worker.
        Disconnects Playwright, stops the event loop, and joins the thread.
        Called from session cleanup (may block briefly).
        """
        try:
            future = asyncio.run_coroutine_threadsafe(self._state.disconnect(), self._loop)
            future.result(timeout=5.0)
        except Exception:
            pass
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=5.0)


# ──────────────────────────────────────────────────────────────────────────────
# ContextVar — task-local BrowserWorker reference
# ──────────────────────────────────────────────────────────────────────────────

_session_browser: ContextVar[BrowserWorker | None] = ContextVar("session_browser", default=None)


def set_session_browser(browser: BrowserWorker) -> Token:
    """Call at the start of each Session Task to bind its BrowserWorker."""
    return _session_browser.set(browser)


def reset_session_browser(token: Token) -> None:
    """Call at the end of each Session Task to clean up."""
    _session_browser.reset(token)


def get_session_browser() -> BrowserWorker | None:
    """Returns the BrowserWorker for the current session context, or None."""
    return _session_browser.get()


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────


async def get_page() -> Page | None:
    """Get the active Playwright page for the current session."""
    browser = get_session_browser()
    if browser is None:
        return None
    return await browser.get_page()


async def browser_launch() -> None:
    """Launch the browser for the current session."""
    browser = get_session_browser()
    if browser is None:
        raise ToolException("No BrowserWorker in session context. Was set_session_browser called?")
    await browser.launch()


async def browser_disconnect() -> None:
    """Disconnect the browser for the current session."""
    browser = get_session_browser()
    if browser is None:
        return
    await browser.disconnect()


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


async def _apply_stealth(context: BrowserContext) -> None:
    stealth = Stealth()
    await stealth.apply_stealth_async(context)


def _wait_for_port(host: str, port: int, timeout: float = 1000) -> bool:
    deadline = time.time() + timeout / 1000
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (socket.error, OSError):
            time.sleep(0.2)
    return False
