import asyncio
from typing import Any

import socketio

from hallw.core import AgentRenderer
from hallw.tools import ToolResult, parse_tool_response
from hallw.utils import Events, logger, subscribe, unsubscribe


class SocketAgentRenderer(AgentRenderer):
    """
    Socket.IO-based renderer optimized for single-user Electron applications.
    Handles real-time UI updates for LLM tokens, tool executions, and system events.
    """

    def __init__(self, sio: socketio.AsyncServer, sid: str, main_loop=None) -> None:
        super().__init__()
        self.sio = sio
        self.sid = sid  # The unique session ID for the connected client
        self.main_loop = main_loop or asyncio.get_event_loop()
        self._current_response = ""

        # Track execution states for UI components (e.g., Sidebar)
        self._tool_states: list[dict[str, Any]] = []
        self._active_tools: dict[str, dict[str, Any]] = {}

        self._setup_event_subscriptions()

    def _setup_event_subscriptions(self) -> None:
        """Subscribe to global agent events and route them to the socket."""
        subscribe(Events.CAPTCHA_DETECTED, self._on_captcha_detected)
        subscribe(Events.CAPTCHA_RESOLVED, self._on_captcha_resolved)
        subscribe(Events.STAGE_STARTED, self._on_stage_started)
        subscribe(Events.SCRIPT_CONFIRM_REQUESTED, self._on_script_confirm_requested)
        subscribe(Events.TOOL_PLAN_UPDATED, self._on_tool_plan_updated)

    def cleanup(self):
        """Unsubscribe from events to prevent memory leaks when the renderer is destroyed."""
        unsubscribe(Events.CAPTCHA_DETECTED, self._on_captcha_detected)
        unsubscribe(Events.CAPTCHA_RESOLVED, self._on_captcha_resolved)
        unsubscribe(Events.STAGE_STARTED, self._on_stage_started)
        unsubscribe(Events.SCRIPT_CONFIRM_REQUESTED, self._on_script_confirm_requested)
        unsubscribe(Events.TOOL_PLAN_UPDATED, self._on_tool_plan_updated)

    async def emit(self, event: str, data: Any = None):
        """Asynchronous helper to send data to the frontend via Socket.IO."""
        try:
            await self.sio.emit(event, data, room=self.sid)
        except Exception as e:
            logger.error(f"Socket Emit Error: {e}")

    def _fire_event(self, event: str, data: Any = None):
        """
        Thread-safe wrapper to trigger an async emit from a synchronous context.
        Essential for callbacks running inside worker threads.
        """
        if self.main_loop and self.main_loop.is_running():
            asyncio.run_coroutine_threadsafe(self.emit(event, data), self.main_loop)

    # --- LLM Callback Handlers ---

    def on_llm_start(self, **kwargs) -> None:
        """Reset buffer and notify frontend that AI has started generating a response."""
        self._current_response = ""
        self._fire_event("ai_response_start")

    def on_llm_chunk(self, chunk: Any) -> None:
        """Extract text from the stream and emit tokens to the ChatArea in real-time."""
        text = self._extract_text(chunk)
        if text:
            self._current_response += text
            self._fire_event("llm_new_token", text)

    def on_llm_end(self, **kwargs) -> None:
        """Notify frontend that the current LLM stream has finished."""
        if self._current_response:
            logger.info(f"HALLW: {self._current_response}")
        self._fire_event("ai_response_end")

    # --- Tool Execution Handlers (Used by Sidebar.jsx) ---

    def on_tool_start(self, run_id: str, name: str, args: Any) -> None:
        """Register a new tool execution and update the UI state."""
        state = {"name": name, "status": "running", "args": str(args), "result": ""}
        self._tool_states.append(state)
        if run_id:
            self._active_tools[run_id] = state
        self._emit_tool_states()

    def on_tool_end(self, run_id: str, name: str, output: Any) -> None:
        """Finalize a tool execution with success status and result data."""
        parsed_output = parse_tool_response(output)
        status = "success" if parsed_output.get("success", False) else "error"
        logger.info(self._build_log_message(name, parsed_output))

        if run_id and run_id in self._active_tools:
            self._active_tools[run_id]["result"] = str(output)
            self._active_tools[run_id]["status"] = status
            self._active_tools.pop(run_id)
        self._emit_tool_states()

    def on_tool_error(self, run_id: str, name: str, error: Any) -> None:
        """Handle tool failures and push error messages to the frontend."""
        logger.error(f"❌ Tool {name} Error: {error[:200]}")
        if run_id and run_id in self._active_tools:
            self._active_tools[run_id]["result"] = str(error)
            self._active_tools[run_id]["status"] = "error"
            self._active_tools.pop(run_id)
        self._fire_event("tool_error", str(error))
        self._emit_tool_states()

    def on_fatal_error(self, run_id: str, name: str, error: Any) -> None:
        """Handle fatal agent errors."""
        logger.critical(f"FATAL AGENT ERROR: {name} - {error}")
        self._fire_event("fatal_error", str(error))

    # --- Internal Helpers ---

    def _emit_tool_states(self):
        """Push the full list of tool executions to update the Sidebar component."""
        self._fire_event("tool_states_updated", self._tool_states)

    def _on_captcha_detected(self, data: dict):
        self._fire_event("captcha_detected", data)

    def _on_captcha_resolved(self, data: dict):
        self._fire_event("captcha_resolved", data)

    def _on_stage_started(self, data: dict):
        """Callback for high-level plan stage changes."""
        self._fire_event("stage_started", data)

    def _on_script_confirm_requested(self, data: dict):
        """Trigger the Safety Confirmation modal in the ChatArea."""
        self._fire_event("script_confirm_requested", data)

    def _on_tool_plan_updated(self, data: dict):
        """Forward partial plan updates to the frontend."""
        self._fire_event("tool_plan_updated", data)

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

    def _build_log_message(self, name: str, parsed_output: ToolResult) -> str:
        sign = "✅" if parsed_output.get("success", False) else "❌"
        data = parsed_output.get("message", "")[:200] + ("..." if len(parsed_output.get("message", "")) > 200 else "")
        return f"{sign} Tool {name}: {data}"
