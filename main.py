import os
import subprocess
import sys
import threading
import warnings

import psutil

from hallw.server.server import main as server_main
from hallw.utils import logger

# Ignore specific warnings from LangSmith about UUID v7
warnings.filterwarnings("ignore", message=".*LangSmith now uses UUID v7.*")


def _patch_windows_asyncio():
    """Fix RuntimeError when closing asyncio event loop on Windows"""
    if sys.platform.startswith("win"):
        from asyncio.proactor_events import _ProactorBasePipeTransport

        def silence_event_loop_closed(self):
            pass

        _ProactorBasePipeTransport.__del__ = silence_event_loop_closed  # type: ignore


def kill_process_on_port(port: int):
    """Find and kill any process listening on the specified port."""
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            for conn in proc.connections(kind="inet"):
                if conn.laddr.port == port:
                    logger.warning(f"Port {port} is in use by {proc.info['name']} (PID: {proc.info['pid']}).")
                    proc.terminate()
                    proc.wait(timeout=3)
                    logger.info(f"Process {proc.info['pid']} terminated.")
                    return
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def run_frontend():
    """Run npm run dev in the frontend directory."""
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")

    try:
        subprocess.check_call(["npm", "run", "dev"], cwd=frontend_dir, shell=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Frontend failed: {e}")
    except KeyboardInterrupt:
        pass


def main():
    _patch_windows_asyncio()

    # Check and clean up port 8000
    kill_process_on_port(8000)

    logger.info("Starting HALLW Development Environment...")

    # 1. Start Backend in a separate thread
    frontend_thread = threading.Thread(target=run_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()

    # 2. Start Backend (runs in main thread)
    try:
        server_main()
    except KeyboardInterrupt:
        logger.info("Stopping...")


if __name__ == "__main__":
    main()
