import asyncio
import json
from typing import Any

import socketio

from hallw.core import AgentRenderer
from hallw.utils import config, logger


class SocketRenderer(AgentRenderer):
    def __init__(self, sio: socketio.AsyncServer, sid: str, main_loop: asyncio.AbstractEventLoop) -> None:
        super().__init__()
        self.sio, self.sid, self.main_loop = sio, sid, main_loop
        self._current_response = ""
        self._pending_confirmation: dict | None = None

    async def emit(self, event: str, data: Any = None):
        try:
            await self.sio.emit(event, data, room=self.sid)
        except Exception as e:
            logger.error(f"Socket Error: {e}")

    def _fire(self, event: str, data: Any = None):
        try:
            asyncio.run_coroutine_threadsafe(self.emit(event, data), self.main_loop)
        except RuntimeError:
            logger.warning(f"No main loop for {event}")

    def on_task_started(self):
        self._fire("task_started")

    def on_task_finished(self):
        self._fire("task_finished")

    def on_llm_start(self):
        self._current_response = ""
        self._fire("llm_started")

    def on_llm_chunk(self, text: str, reasoning: str):
        if reasoning:
            self._fire("llm_new_reasoning", reasoning)
        if text:
            self._current_response += text
            self._fire("llm_new_text", text)

    def on_llm_end(self):
        if self._current_response:
            max_len = config.logging_max_chars
            self._current_response = self._current_response.replace("\n", " ").strip()
            logger.info(f"AI: {self._current_response[:max_len]}...")
        self._fire("llm_finished")

    def on_tool_start(self, run_id: str, name: str, args: Any):
        args_str = str(args)
        try:
            args_str = json.dumps(args, ensure_ascii=False)
        except Exception:
            pass
        self._fire("tool_state_update", {"run_id": run_id, "tool_name": name, "status": "running", "args": args_str})

    def on_tool_end(self, run_id: str, name: str, output: Any, is_success: bool, log_msg: str):
        logger.info(log_msg)

        result_str = str(output)
        if isinstance(output, (dict, list)):
            try:
                result_str = json.dumps(output, ensure_ascii=False)
            except Exception:
                result_str = str(output)

        self._fire(
            "tool_state_update",
            {"run_id": run_id, "status": "success" if is_success else "error", "result": result_str},
        )

    def on_tool_error(self, run_id: str, name: str, error: str):
        logger.error(f"Tool {name} Error: {error}")
        self._fire("tool_state_update", {"run_id": run_id, "status": "error", "result": error})

    def on_fatal_error(self, run_id: str, name: str, error: str):
        logger.critical(f"Fatal: {name} - {error}")
        self._fire("fatal_error", error)

    def on_stages_built(self, data: dict) -> None:
        """Forward partial plan updates to the frontend."""
        self._fire("stages_built", data)

    def on_stage_started(self, data: dict):
        self._fire("stage_started", data)

    def on_stages_completed(self, data: dict):
        self._fire("stages_completed", data)

    def on_stages_edited(self, data: dict):
        self._fire("stages_edited", data)

    # User Input / Confirmation
    async def on_request_confirmation(self, request_id: str, timeout: int, message: str) -> str:
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._pending_confirmation = {"request_id": request_id, "future": future, "loop": loop}
        self._fire("request_confirmation", {"request_id": request_id, "message": message, "timeout": timeout})
        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            return "timeout"
        finally:
            self._pending_confirmation = None

    def on_resolve_confirmation(self, request_id: str, status: str):
        if self._pending_confirmation and self._pending_confirmation["request_id"] == request_id:
            future = self._pending_confirmation["future"]
            loop = self._pending_confirmation.get("loop")
            if not future.done():
                if loop:
                    loop.call_soon_threadsafe(future.set_result, status)
                else:
                    future.set_result(status)

    async def on_request_user_decision(self, prompt: str, choices: list[str] = None, timeout: int = 300) -> str:
        """Trigger the RuntimeInput modal in the UI and wait for result."""
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        request_id = f"input_{id(future)}"
        self._pending_confirmation = {"request_id": request_id, "future": future, "loop": loop}

        self._fire(
            "request_user_decision",
            {
                "request_id": request_id,
                "message": prompt,
                "choices": choices,
                "timeout": timeout,
            },
        )

        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            return "timeout"
        finally:
            if self._pending_confirmation and self._pending_confirmation["request_id"] == request_id:
                self._pending_confirmation = None

    def on_resolve_user_decision(self, request_id: str, status: str, value: str = None) -> None:
        """Resolve a pending user input request from the frontend."""
        if self._pending_confirmation and self._pending_confirmation["request_id"] == request_id:
            future = self._pending_confirmation["future"]
            loop = self._pending_confirmation.get("loop")
            if not future.done():
                res_val = value if status == "submitted" and value is not None else status
                if loop:
                    loop.call_soon_threadsafe(future.set_result, res_val)
                else:
                    future.set_result(res_val)

    async def on_request_cdp_page(self, timeout: int = 30, headless: bool = True, user_data_dir: str = None) -> str:
        """Ask the frontend to open a new BrowserWindow for CDP, wait for success."""
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        request_id = f"cdp_{id(future)}"
        self._pending_confirmation = {"request_id": request_id, "future": future, "loop": loop}
        self._fire("request_cdp_page", {"request_id": request_id, "headless": headless, "userDataDir": user_data_dir})
        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            return "timeout"
        finally:
            self._pending_confirmation = None

    def on_resolve_cdp_page(self, status: str):
        if self._pending_confirmation and self._pending_confirmation["request_id"].startswith("cdp_"):
            future = self._pending_confirmation["future"]
            loop = self._pending_confirmation.get("loop")
            if not future.done():
                if loop:
                    loop.call_soon_threadsafe(future.set_result, status)
                else:
                    future.set_result(status)
