import asyncio
import os
import shutil
import socket
import subprocess
import tempfile
import time
from contextlib import asynccontextmanager
from typing import Optional

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
    get_browser,
    get_chrome_process,
    get_context,
    get_pw,
    get_temp_user_data_dir,
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

    chrome_already_running = False
    try:
        chrome_already_running = _wait_for_port("127.0.0.1", CDP_PORT, timeout=CDP_TIMEOUT)
    except Exception:
        chrome_already_running = False

    # Initiate playwright instance
    pw = await async_playwright().start()
    set_pw(pw)

    # Try to reuse existing Chrome instance
    if chrome_already_running:
        endpoint = f"http://127.0.0.1:{CDP_PORT}"
        try:
            browser = await pw.chromium.connect_over_cdp(endpoint)
            set_browser(browser)
            # Create a new context
            context = await browser.new_context(
                viewport={"width": PW_WINDOW_WIDTH, "height": PW_WINDOW_HEIGHT}
            )
            await set_context(context)
            set_chrome_process(None)  # Since we didn't start it

            return "Connected to existing Chrome instance."

        except Exception as e:
            raise ToolException(f"Failed to connect to existing Chrome via CDP: {e}")

    # Launch new Chrome instance
    chrome_path = _find_chrome_executable()
    # If local browser not preferred or not found, use Playwright Chromium
    if not PREFER_LOCAL_CHROME or chrome_path is None:
        try:
            args = _build_chrome_args()
            browser = await pw.chromium.launch(args=args)
            set_browser(browser)
            context = (
                browser.contexts[0]
                if browser.contexts
                else await browser.new_context(
                    viewport={"width": PW_WINDOW_WIDTH, "height": PW_WINDOW_HEIGHT}
                )
            )
            await set_context(context)
        except Exception:
            _cleanup_chrome_process()
            raise ToolException(
                "Playwright Chromium not installed, " "run `playwright install chromium` first"
            )
        set_chrome_process(None)  # It's managed by Playwright
        return "Playwright Chromium launched"
    # Launch local Chrome with CDP
    else:
        args = _build_chrome_args(chrome_path)

        process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        set_chrome_process(process)

        if not _wait_for_port("127.0.0.1", CDP_PORT, CDP_TIMEOUT):
            _cleanup_chrome_process()
            raise ToolException("Local Chrome failed to start with CDP.")

        endpoint = f"http://127.0.0.1:{CDP_PORT}"
        browser = await pw.chromium.connect_over_cdp(endpoint)
        set_browser(browser)
        # Use default context
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        await set_context(context)
        set_chrome_process(process)

        return "Local Chrome with CDP started."


async def browser_close() -> str:
    """Close Playwright session and optionally leave Chrome running."""

    if KEEP_PAGE_OPEN:
        logger.info("KEEP_PAGE_OPEN is enabled; leaving page open.")
        return "KEEP_PAGE_OPEN is enabled; leaving page open"
    else:
        context = get_context()
        if context is None:
            return "Browser is not launched"
        pages = context.pages
        for page in pages:
            try:
                await page.close()
            except Exception:
                continue
        try:
            await context.close()
            browser = get_browser()
            if browser and len(browser.contexts) == 0:
                await browser.close()
                _cleanup_chrome_process()
        except Exception:
            pass

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
            # Write current PID to lock file
            os.write(fd, str(os.getpid()).encode())
            break
        except FileExistsError:
            # Check if the lock is stale or belongs to a dead process
            try:
                if os.path.exists(lock_path):
                    # Check if lock is stale by time
                    if time.time() - os.path.getmtime(lock_path) > 60:
                        os.remove(lock_path)
                        continue

                    # Check if lock belongs to this process (re-entrant/cleanup)
                    # or a dead process
                    try:
                        with open(lock_path, "r") as f:
                            pid_str = f.read().strip()
                        if pid_str:
                            pid = int(pid_str)
                            if pid == os.getpid():
                                # Lock belongs to us (likely from a killed thread), reclaim it
                                os.remove(lock_path)
                                continue
                    except (ValueError, OSError):
                        pass
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
            with socket.create_connection((host, port), timeout=1):
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

    time.sleep(1)  # Ensure process has time to terminate

    temp_user_data_dir = get_temp_user_data_dir()
    if temp_user_data_dir and os.path.exists(temp_user_data_dir):
        shutil.rmtree(temp_user_data_dir, ignore_errors=True)
        set_temp_user_data_dir(None)


def _build_chrome_args(chrome_path: str = None) -> list:
    """Build Chrome command-line arguments."""
    if CHROME_USER_DATA_DIR:
        user_data_dir = os.path.abspath(CHROME_USER_DATA_DIR)  # Chrome accepts only absolute paths
    else:
        user_data_dir = tempfile.mkdtemp()
        set_temp_user_data_dir(user_data_dir)

    args = []

    if chrome_path:
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
    else:
        args = [
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
