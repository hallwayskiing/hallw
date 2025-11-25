import asyncio
import threading


class AgentEventLoop:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start(self):
        """Start persistent event loop in background thread."""
        self.thread.start()

    def submit(self, coro):
        """Thread-safe submission of asyncio coroutine."""
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def stop(self):
        """Stop the persistent event loop."""
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()
