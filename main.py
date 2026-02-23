import os
import signal
import subprocess
import sys
import threading
import warnings

import psutil

# Ignore specific warnings from LangSmith about UUID v7
warnings.filterwarnings("ignore", message=".*LangSmith now uses UUID v7.*")
# Ignore specific warnings from LangChain about Pydantic V1 and Python 3.14+
warnings.filterwarnings("ignore", message=".*Core Pydantic V1 functionality isn't compatible with Python 3.14.*")


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
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            proc.kill()
                        return
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
    except Exception:
        pass


def run_frontend() -> subprocess.Popen | None:
    """Run npm run dev in the frontend directory."""
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")

    try:
        return subprocess.Popen(["bun", "dev"], cwd=frontend_dir, shell=True)
    except Exception:
        return None


def main():
    from hallw.server.server import main as server_main
    from hallw.utils import logger

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
