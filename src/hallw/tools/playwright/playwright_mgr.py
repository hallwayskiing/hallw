import asyncio
import os
import shutil
import socket
import subprocess
import tempfile
import time
from contextlib import asynccontextmanager
from typing import Optional

import psutil
from langchain_core.tools import ToolException
from playwright.async_api import async_playwright

from hallw.utils import logger

from .playwright_state import (
    CDP_PORT,
    CDP_TIMEOUT,
    CHROME_USER_DATA_DIR,
    HEADLESS_MODE,
    KEEP_PAGE_OPEN,
    PREFER_LOCAL_CHROME,
    PW_WINDOW_HEIGHT,
    PW_WINDOW_WIDTH,
    add_page,
    get_all_pages,
    get_browser,
    get_chrome_process,
    get_context,
    get_pw,
    get_temp_user_data_dir,
    launched,
    reset_all,
    set_browser,
    set_chrome_process,
    set_context,
    set_pw,
    set_temp_user_data_dir,
)

LOCK_FILE = os.path.join(tempfile.gettempdir(), "hallw_playwright_mgr.lock")


async def browser_launch() -> str:
    """Open Chrome or reuse an existing instance and connect via CDP.

    Returns:
        Status message
    """
    async with async_file_lock(LOCK_FILE):
        chrome_already_running = False
        try:
            chrome_already_running = _wait_for_port("127.0.0.1", CDP_PORT, timeout=CDP_TIMEOUT)
        except Exception:
            chrome_already_running = False

        # Try to reuse existing Chrome instance
        if chrome_already_running:
            endpoint = f"http://127.0.0.1:{CDP_PORT}"
            try:
                pw = await async_playwright().start()
                set_pw(pw)
                browser = await pw.chromium.connect_over_cdp(endpoint)
                set_browser(browser)
                context = browser.contexts[0] if browser.contexts else await browser.new_context()
                set_context(context)
                page = await context.new_page()
                await add_page(page)
                set_chrome_process(None)  # Since we didn't start it

                return "Connected to existing Chrome instance."

            except Exception as e:
                raise ToolException(f"Failed to connect to existing Chrome via CDP: {e}")

        # Launch new Chrome instance
        chrome_path = _find_chrome_executable()
        # If local browser not preferred or not found, use Playwright Chromium
        if not PREFER_LOCAL_CHROME or chrome_path is None:
            pw = await async_playwright().start()
            set_pw(pw)
            try:
                if CHROME_USER_DATA_DIR:
                    persistent_context = await pw.chromium.launch_persistent_context(
                        headless=HEADLESS_MODE,
                        user_data_dir=CHROME_USER_DATA_DIR,
                        viewport={"width": PW_WINDOW_WIDTH, "height": PW_WINDOW_HEIGHT},
                    )
                    set_browser(persistent_context.browser)
                    set_context(persistent_context)
                    page = (
                        persistent_context.pages[0]
                        if persistent_context.pages
                        else await persistent_context.new_page()
                    )
                    await add_page(page)
                else:
                    browser = await pw.chromium.launch(headless=HEADLESS_MODE)
                    set_browser(browser)
                    context = (
                        browser.contexts[0]
                        if browser.contexts
                        else await browser.new_context(
                            viewport={"width": PW_WINDOW_WIDTH, "height": PW_WINDOW_HEIGHT}
                        )
                    )
                    set_context(context)
                    page = context.pages[0] if context.pages else await context.new_page()
                    await add_page(page)
            except Exception:
                raise ToolException(
                    "Playwright Chromium not installed, " "run `playwright install chromium` first"
                )
            set_chrome_process(None)  # It's managed by Playwright
            return "Playwright Chromium launched"

        args = _build_chrome_args(chrome_path)

        process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        set_chrome_process(process)

        if not _wait_for_port("127.0.0.1", CDP_PORT, CDP_TIMEOUT):
            _cleanup_chrome_process()
            raise ToolException("Local Chrome failed to start with CDP.")

        endpoint = f"http://127.0.0.1:{CDP_PORT}"

        pw = await async_playwright().start()
        set_pw(pw)
        browser = await pw.chromium.connect_over_cdp(endpoint)
        set_browser(browser)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        set_context(context)
        page = context.pages[0] if context.pages else await context.new_page()
        await add_page(page)
        set_chrome_process(process)

        return "Local Chrome with CDP started."


async def browser_close() -> str:
    """Close Playwright session and optionally leave Chrome running."""
    if not launched():
        return "Browser not launched"

    async with async_file_lock(LOCK_FILE):
        if KEEP_PAGE_OPEN:
            logger.info("KEEP_PAGE_OPEN is enabled; leaving page open.")
        else:
            pages = get_all_pages()
            try:
                for page in pages:
                    await page.close()
            except Exception:
                pass
            context = get_context()
            if context and len(context.pages) == 0:
                try:
                    browser = get_browser()
                    await browser.close()
                except Exception:
                    pass
                _cleanup_chrome_process()

        pw = get_pw()
        if pw is not None:
            try:
                await pw.stop()
            except Exception:
                pass
        reset_all()

        return "Browser successfully closed"


@asynccontextmanager
async def async_file_lock(lock_path: str, timeout: float = 30.0):
    """Prevent concurrent browser launches using a file lock."""
    start_time = time.time()
    fd = None
    while True:
        try:
            # Try to create the file in exclusive mode (atomic operation)
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            break
        except FileExistsError:
            # Check if the lock has expired (e.g., more than 60 seconds) to prevent deadlock
            try:
                if os.path.exists(lock_path) and time.time() - os.path.getmtime(lock_path) > 60:
                    os.remove(lock_path)
                    continue
            except OSError:
                pass  # The file might have been deleted by another process

            if time.time() - start_time >= timeout:
                raise ToolException(f"Timeout waiting for browser lock: {lock_path}")
            await asyncio.sleep(0.1)

    try:
        yield
    finally:
        if fd is not None:
            os.close(fd)
            try:
                if os.path.exists(lock_path):
                    os.remove(lock_path)
            except OSError:
                pass


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
            with socket.create_connection((host, port), timeout=100):
                return True
        except (socket.error, OSError):
            time.sleep(0.2)
    return False


def _cleanup_chrome_process():
    """Terminate Chrome process and clean up temporary directory."""
    proc = get_chrome_process()
    if proc:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        set_chrome_process(None)
    else:
        existing_pid = _find_existing_chrome_process(CDP_PORT)
        if existing_pid:
            try:
                p = psutil.Process(existing_pid)
                p.terminate()
                p.wait(timeout=5)
            except Exception:
                try:
                    p.kill()
                except Exception:
                    pass

    time.sleep(1)  # Ensure process has time to terminate

    temp_user_data_dir = get_temp_user_data_dir()
    if temp_user_data_dir and os.path.exists(temp_user_data_dir):
        shutil.rmtree(temp_user_data_dir, ignore_errors=True)
        set_temp_user_data_dir(None)


def _find_existing_chrome_process(port: int = CDP_PORT) -> Optional[int]:
    """Find the PID of an already running Chrome CDP process."""
    try:
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmdline = proc.info.get("cmdline", [])
                if cmdline and "chrome" in proc.info["name"].lower():
                    if any(f"--remote-debugging-port={port}" in arg for arg in cmdline):
                        return int(proc.info["pid"])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        logger.warning(f"Failed to search for Chrome process: {e}")
    return None


def _build_chrome_args(chrome_path: str) -> list:
    """Build Chrome command-line arguments."""
    if CHROME_USER_DATA_DIR:
        user_data_dir = os.path.abspath(CHROME_USER_DATA_DIR)  # Chrome accepts only absolute paths
    else:
        user_data_dir = tempfile.mkdtemp()
        set_temp_user_data_dir(user_data_dir)

    args = [
        chrome_path,
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--window-size={}x{}".format(PW_WINDOW_WIDTH, PW_WINDOW_HEIGHT),
        "--no-default-browser-check",
        "--exclude-switches=enable-automation",
        "--disable-dev-shm-usage",
        "--disable-features=IsolateOrigins,site-per-process",
    ]
    if HEADLESS_MODE:
        args.append("--headless=new")
    return args
