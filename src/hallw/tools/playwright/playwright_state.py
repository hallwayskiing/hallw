import subprocess
from typing import List, Optional

from playwright.async_api import Browser, BrowserContext, Page, Playwright
from playwright_stealth.stealth import Stealth

from hallw.utils import config

# Configuration constants
PREFER_LOCAL_CHROME = config.prefer_local_chrome
CHROME_USER_DATA_DIR = config.chrome_user_data_dir
CDP_PORT = config.cdp_port
HEADLESS_MODE = config.pw_headless_mode
PW_WINDOW_WIDTH = config.pw_window_width
PW_WINDOW_HEIGHT = config.pw_window_height
KEEP_PAGE_OPEN = config.keep_page_open
SEARCH_RESULT_COUNT = config.search_result_count
MAX_PAGE_CONTENT_CHARS = config.max_page_content_chars
MANUAL_CAPTCHA_TIMEOUT = config.manual_captcha_timeout
GOTO_TIMEOUT = config.pw_goto_timeout
CLICK_TIMEOUT = config.pw_click_timeout
CDP_TIMEOUT = config.pw_cdp_timeout

# Singleton state
_launched = False
_pw: Optional[Playwright] = None
_browser: Optional[Browser] = None
_context: Optional[BrowserContext] = None
_pages: Optional[List[Page]] = None
_chrome_process: Optional[subprocess.Popen] = None
_temp_user_data_dir: Optional[str] = None


def launched() -> bool:
    return _launched


async def get_page(index: int) -> Optional[Page]:
    await ensure_context()

    if index >= len(_pages):
        return None

    return _pages[index]


async def add_page(page: Page) -> int:
    global _pages
    if _pages is None:
        _pages = []

    stealth = Stealth()
    await stealth.apply_stealth_async(page)
    _pages.append(page)
    return len(_pages) - 1


async def ensure_context() -> None:
    global _launched
    _launched = True

    if _pages is None:
        from .playwright_mgr import browser_launch

        await browser_launch()


def get_all_pages() -> Optional[List[Page]]:
    return _pages


def get_browser() -> Browser:
    return _browser


def set_browser(browser: Browser):
    global _browser
    _browser = browser


def get_context() -> BrowserContext:
    return _context


def set_context(context: BrowserContext):
    global _context
    _context = context


def get_pw() -> Playwright:
    return _pw


def set_pw(pw: Playwright):
    global _pw
    _pw = pw


def get_chrome_process() -> Optional[subprocess.Popen]:
    return _chrome_process


def set_chrome_process(proc: Optional[subprocess.Popen]):
    global _chrome_process
    _chrome_process = proc


def get_temp_user_data_dir() -> Optional[str]:
    return _temp_user_data_dir


def set_temp_user_data_dir(dir_path: Optional[str]):
    global _temp_user_data_dir
    _temp_user_data_dir = dir_path


def reset_all():
    """Reset all singletons to None."""
    global _pw, _browser, _context, _pages, _chrome_process, _temp_user_data_dir, _launched
    _launched = False
    _pw = None
    _browser = None
    _context = None
    _pages = None
    _chrome_process = None
    _temp_user_data_dir = None
