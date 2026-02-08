import asyncio
from typing import Any, Optional

import socketio

from hallw.core import AgentRenderer
from hallw.tools import parse_tool_response
from hallw.utils import logger


class SocketAgentRenderer(AgentRenderer):
    """
    Socket.IO-based renderer optimized for single-user Electron applications.
    Handles real-time UI updates for LLM tokens, tool executions, and system events.

    Now runs in a single event loop (uvicorn's), eliminating cross-loop complexity.
    """

    def __init__(self, sio: socketio.AsyncServer, sid: str) -> None:
        super().__init__()
        self.sio = sio
        self.sid = sid  # The unique session ID for the connected client
        self._current_response = ""
        self._active_tool: Optional[dict[str, Any]] = None
        self._pending_confirmation: Optional[dict[str, Any]] = None

    async def emit(self, event: str, data: Any = None):
        """Asynchronous helper to send data to the frontend via Socket.IO."""
        try:
            await self.sio.emit(event, data, room=self.sid)
        except Exception as e:
            logger.error(f"Socket Emit Error: {e}")

    def _fire_event(self, event: str, data: Any = None):
        """
        Fire an event to the frontend. Since we're now in a single event loop,
        we can use asyncio.create_task() directly.
        """
        try:
            asyncio.create_task(self.emit(event, data))
        except RuntimeError:
            # No running event loop, log and skip
            logger.warning(f"Cannot fire event {event}: no running event loop")

    # --- LLM Callback Handlers ---

    def on_llm_start(self) -> None:
        """Reset buffer and notify frontend that AI has started generating a response."""
        self._current_response = ""
        self._fire_event("ai_response_start")

    def on_llm_chunk(self, chunk: Any) -> None:
        """Extract text from the stream and emit tokens to the ChatArea in real-time."""
        text = self._extract_text(chunk)
        if text:
            self._current_response += text
            self._fire_event("llm_new_token", text)

    def on_llm_end(self) -> None:
        """Notify frontend that the current LLM stream has finished."""
        if self._current_response:
            logger.info(f"HALLW: {self._current_response}")
        self._fire_event("ai_response_end")

    # --- Tool Execution Handlers (Used by Sidebar.jsx) ---

    def on_tool_start(self, run_id: str, name: str, args: Any) -> None:
        """Register a new tool execution and emit an incremental update."""
        state = {
            "run_id": run_id,  # Ensure run_id is included for matching
            "tool_name": name,
            "status": "running",
            "args": str(args),
            "result": "",
        }

        self._active_tool = state

        # Incremental update: send only the new state object
        self._fire_event("tool_state_update", state)

    def on_tool_end(self, run_id: str, name: str, output: Any) -> None:
        """Finalize a tool execution and emit an incremental update."""
        parsed_output = parse_tool_response(output)
        status = "success" if parsed_output.get("success", False) else "error"

        logger.info(self._build_log_message(name, parsed_output))

        state = self._active_tool
        if state:
            state["result"] = str(output)
            state["status"] = status
        self._active_tool = None

        if state:
            # Incremental update: send the updated state object
            self._fire_event("tool_state_update", state)

    def on_tool_error(self, run_id: str, name: str, error: Any) -> None:
        """Handle tool failures and emit an incremental update."""
        logger.error(f"❌ Tool {name} Error: {str(error)[:200]}")

        state = self._active_tool
        if state:
            state["result"] = str(error)
            state["status"] = "error"
        self._active_tool = None

        if state:
            # Incremental update
            self._fire_event("tool_state_update", state)

    def on_fatal_error(self, run_id: str, name: str, error: Any) -> None:
        """Handle fatal agent errors."""
        logger.critical(f"FATAL AGENT ERROR: {name} - {error}")

        state = self._active_tool
        if state:
            state["result"] = str(error)
            state["status"] = "error"
        self._active_tool = None

        if state:
            # Incremental update
            self._fire_event("tool_state_update", state)
        self._fire_event("fatal_error", str(error))

    # --- Domain Specific Events ---

    def on_stage_started(self, data: dict) -> None:
        """Callback for high-level plan stage changes."""
        self._fire_event("stage_started", data)

    def on_stage_completed(self, data: dict) -> None:
        """Callback for high-level plan stage completion."""
        self._fire_event("stage_completed", data)

    def on_tool_plan_updated(self, data: dict) -> None:
        """Forward partial plan updates to the frontend."""
        self._fire_event("tool_plan_updated", data)

    async def on_request_confirmation(self, request_id: str, timeout: int, message: str) -> str:
        """
        Trigger the Confirmation modal in the ChatArea.
        """
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._pending_confirmation = {"request_id": request_id, "future": future}

        self._fire_event("request_confirmation", {"request_id": request_id, "message": message, "timeout": timeout})

        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            return "timeout"
        finally:
            self._pending_confirmation = None

    def on_resolve_confirmation(self, request_id: str, status: str) -> None:
        """Resolve a pending confirmation request from the frontend."""
        if self._pending_confirmation and self._pending_confirmation["request_id"] == request_id:
            future = self._pending_confirmation["future"]
            if not future.done():
                future.set_result(status)

    async def on_request_user_input(self, prompt: str, timeout: int) -> str:
        """
        Trigger the RuntimeInput modal in the ChatArea.
        """
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        request_id = f"input_{id(future)}"
        self._pending_confirmation = {"request_id": request_id, "future": future}

        self._fire_event("request_user_input", {"request_id": request_id, "message": prompt, "timeout": timeout})

        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            return "timeout"
        finally:
            if self._pending_confirmation and self._pending_confirmation["request_id"] == request_id:
                self._pending_confirmation = None

    def on_resolve_user_input(self, request_id: str, status: str, value: str = None) -> None:
        """Resolve a pending user input request from the frontend."""
        if self._pending_confirmation and self._pending_confirmation["request_id"] == request_id:
            future = self._pending_confirmation["future"]
            if not future.done():
                if status == "submitted" and value is not None:
                    future.set_result(value)
                else:
                    future.set_result(status)

    # --- Internal Helpers ---

    def _extract_text(self, chunk: Any) -> str:
        """Utility to parse text content from various LLM provider chunk formats."""
        if not chunk:
            return ""

        content = getattr(chunk, "content", chunk)
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join([i if isinstance(i, str) else i.get("text", "") for i in content])
        return str(content)

    def _build_log_message(self, name: str, parsed_output: Any) -> str:
        sign = "✅" if parsed_output.get("success", False) else "❌"
        data = (
            parsed_output.get("message", "")[:200] + ("..." if len(parsed_output.get("message", "")) > 200 else "")
            if parsed_output.get("message")
            else ""
        )
        return f"{sign} Tool {name}: {data}"
