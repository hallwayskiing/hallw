import os
import shutil
import socket
import subprocess
import tempfile
import time
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
    KEEP_BROWSER_OPEN,
    PREFER_LOCAL_CHROME,
    PW_WINDOW_HEIGHT,
    PW_WINDOW_WIDTH,
    get_chrome_process,
    get_pw,
    get_temp_user_data_dir,
    launched,
    reset_all,
    set_browser,
    set_chrome_process,
    set_context,
    set_page,
    set_pw,
    set_temp_user_data_dir,
)


async def browser_launch() -> str:
    """Open Chrome or reuse an existing instance and connect via CDP.

    Returns:
        Status message
    """
    chrome_already_running = False
    try:
        chrome_already_running = wait_for_port("127.0.0.1", CDP_PORT, timeout=CDP_TIMEOUT)
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
            page = context.pages[0] if context.pages else await context.new_page()
            await set_page(page)
            set_chrome_process(None)  # Since we didn't start it

            return f"Connected to existing Chrome instance."

        except Exception as e:
            raise ToolException(f"Failed to connect to existing Chrome via CDP: {e}")

    # Launch new Chrome instance
    chrome_path = find_chrome_executable()
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
                await set_page(page)
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
                await set_page(page)
        except Exception as e:
            raise ToolException(f"Error when launching Playwright Chromium: {e}")
        set_chrome_process(None)  # It's managed by Playwright
        return "Playwright Chromium launched"

    args = build_chrome_args(chrome_path)

    process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    set_chrome_process(process)

    if not wait_for_port("127.0.0.1", CDP_PORT, CDP_TIMEOUT):
        cleanup_chrome_process()
        raise ToolException("Local Chrome failed to start with CDP.")

    endpoint = f"http://127.0.0.1:{CDP_PORT}"

    pw = await async_playwright().start()
    set_pw(pw)
    browser = await pw.chromium.connect_over_cdp(endpoint)
    set_browser(browser)
    context = browser.contexts[0] if browser.contexts else await browser.new_context()
    set_context(context)
    page = context.pages[0] if context.pages else await context.new_page()
    await set_page(page)
    set_chrome_process(process)

    return "Local Chrome with CDP started."


async def browser_close() -> str:
    """Close Playwright session and optionally leave Chrome running."""
    if not launched():
        return "Browser not launched"

    pw = get_pw()

    if pw is not None:
        await pw.stop()
        set_pw(None)
        set_browser(None)
        set_context(None)
        await set_page(None)

    if KEEP_BROWSER_OPEN:
        logger.info("KEEP_BROWSER_OPEN is enabled; leaving Chrome open.")
    else:
        cleanup_chrome_process()

    reset_all()
    return "Browser successfully closed"


def find_chrome_executable() -> Optional[str]:
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


def wait_for_port(host: str, port: int, timeout: float = 1000) -> bool:
    """Wait for a TCP port to become available."""
    deadline = time.time() + timeout / 1000
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=100):
                return True
        except (socket.error, OSError):
            time.sleep(0.2)
    return False


def find_existing_chrome_process(port: int = CDP_PORT) -> Optional[int]:
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


def cleanup_chrome_process():
    """Terminate Chrome process and clean up temporary directory."""
    proc = get_chrome_process()
    if proc is not None:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        set_chrome_process(None)

    time.sleep(1)  # Ensure process has time to terminate

    temp_user_data_dir = get_temp_user_data_dir()
    if temp_user_data_dir and os.path.exists(temp_user_data_dir):
        shutil.rmtree(temp_user_data_dir, ignore_errors=True)
        set_temp_user_data_dir(None)


def build_chrome_args(chrome_path: str) -> list:
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
