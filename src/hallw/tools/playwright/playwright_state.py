import subprocess
from typing import Optional

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
_page: Optional[Page] = None
_chrome_process: Optional[subprocess.Popen] = None
_temp_user_data_dir: Optional[str] = None


def launched() -> bool:
    return _launched


async def get_page() -> Page:
    global _launched
    _launched = True

    if _page is None:
        from .playwright_mgr import browser_launch

        await browser_launch()

    return _page


async def set_page(page: Optional[Page]):
    global _page
    if page is None:
        _page = None
    else:
        s = Stealth()
        await s.apply_stealth_async(page)
        _page = page


def get_browser() -> Optional[Browser]:
    return _browser


def set_browser(browser: Optional[Browser]):
    global _browser
    _browser = browser


def get_context() -> Optional[BrowserContext]:
    return _context


def set_context(context: Optional[BrowserContext]):
    global _context
    _context = context


def get_pw() -> Optional[Playwright]:
    return _pw


def set_pw(pw: Optional[Playwright]):
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
    global _pw, _browser, _context, _page, _chrome_process, _temp_user_data_dir
    _pw = None
    _browser = None
    _context = None
    _page = None
    _chrome_process = None
    _temp_user_data_dir = None
