import os
import signal
import subprocess
import sys
import threading
import warnings
from typing import Optional

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
    try:
        for conn in psutil.net_connections(kind="inet"):
            if conn.laddr.port == port:
                pid = conn.pid
                if pid:
                    try:
                        proc = psutil.Process(pid)
                        logger.warning(f"Port {port} is in use by {proc.name()} (PID: {pid}).")
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                            logger.info(f"Process {pid} terminated.")
                        except psutil.TimeoutExpired:
                            proc.kill()
                            logger.info(f"Process {pid} killed (timeout expired).")
                        return
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
    except Exception as e:
        logger.error(f"Failed to check/kill process on port {port}: {e}")


def run_frontend() -> Optional[subprocess.Popen]:
    """Run npm run dev in the frontend directory."""
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")

    try:
        return subprocess.Popen(["bun", "dev"], cwd=frontend_dir, shell=True)
    except Exception as e:
        logger.error(f"Failed to start frontend: {e}")
        return None


def main():
    _patch_windows_asyncio()

    server_port = 8000
    kill_process_on_port(server_port)

    # 1. Start Frontend in a separate thread
    fe_proc = run_frontend()

    # 2. Start monitor thread for frontend
    def monitor_frontend():
        if fe_proc:
            fe_proc.wait()
            os.kill(os.getpid(), signal.SIGINT)

    monitor_thread = threading.Thread(target=monitor_frontend, daemon=True)
    monitor_thread.start()

    # 2. Start Backend (runs in main thread)
    try:
        server_main()
    except KeyboardInterrupt:
        logger.info("Stopping...")
        if fe_proc:
            fe_proc.terminate()


if __name__ == "__main__":
    main()
