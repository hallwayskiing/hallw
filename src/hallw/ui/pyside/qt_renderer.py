import json
import re
from typing import Any

from PySide6.QtCore import QObject, QThread, Signal

from hallw.core import AgentRenderer, AgentTask
from hallw.tools import parse_tool_response
from hallw.utils import Events, subscribe, unsubscribe


class QtAgentRenderer(QObject, AgentRenderer):
    """Qt-based renderer for agent events with signal-based UI updates."""

    # UI Update Signals
    new_token_received = Signal(str)
    tool_plan_updated = Signal(str)
    tool_execution_updated = Signal(str)
    ai_response_start = Signal()
    tool_error_occurred = Signal(str)
    fatal_error_occurred = Signal(str)
    task_finished = Signal()

    # User action signals
    captcha_detected = Signal(str, int, int)  # engine, page_index, timeout_ms
    captcha_resolved = Signal(str, bool)  # engine, success
    stage_started = Signal(int, int, str)  # stage_index, total_stages, stage_name
    script_confirm_requested = Signal(str, str)  # request_id, command

    # Pre-compiled regex for parsing partial JSON streams (optimization)
    # Captures: "key": "string" OR "key": [primitive/object]
    _PARTIAL_JSON_PATTERN = re.compile(
        r'"([^"]+)"\s*:\s*(?:"([^"\\]*(?:\\.[^"\\]*)*)"|(\[[^\]]*\]|\{[^\}]*\}|[\d.]+|true|false|null))'
    )
    _TRAILING_KEY_PATTERN = re.compile(r'"([^"]+)"\s*:\s*"?([^"{\[]*?)$')

    def __init__(self) -> None:
        # Initialize QObject first, then AgentRenderer
        super().__init__()
        AgentRenderer.__init__(self)

        # State containers
        self._tool_call_buffer: dict[int, dict[str, str]] = {}
        self._tool_states: list[dict[str, Any]] = []
        self._active_tools: dict[str, dict[str, Any]] = {}  # Maps run_id -> state dict reference

        # Subscribe to global events
        self._setup_event_subscriptions()

    def _setup_event_subscriptions(self) -> None:
        """Subscribe to global event bus events."""
        subscribe(Events.CAPTCHA_DETECTED, self._on_captcha_detected)
        subscribe(Events.CAPTCHA_RESOLVED, self._on_captcha_resolved)
        subscribe(Events.STAGE_STARTED, self._on_stage_started)
        subscribe(Events.SCRIPT_CONFIRM_REQUESTED, self._on_script_confirm_requested)

    def _teardown_event_subscriptions(self) -> None:
        """Unsubscribe from global event bus events."""
        unsubscribe(Events.CAPTCHA_DETECTED, self._on_captcha_detected)
        unsubscribe(Events.CAPTCHA_RESOLVED, self._on_captcha_resolved)
        unsubscribe(Events.STAGE_STARTED, self._on_stage_started)
        unsubscribe(Events.SCRIPT_CONFIRM_REQUESTED, self._on_script_confirm_requested)

    def _on_captcha_detected(self, data: dict[str, Any]) -> None:
        """Handle captcha detected event from tools."""
        engine = data.get("engine", "unknown")
        page_index = data.get("page_index", 0)
        timeout_ms = data.get("timeout_ms", 60000)
        self.captcha_detected.emit(engine, page_index, timeout_ms)

    def _on_captcha_resolved(self, data: dict[str, Any]) -> None:
        """Handle captcha resolved event from tools."""
        engine = data.get("engine", "unknown")
        success = data.get("success", True)
        self.captcha_resolved.emit(engine, success)

    def _on_stage_started(self, data: dict[str, Any]) -> None:
        """Handle stage started event from agent."""
        stage_index = data.get("stage_index", 0)
        total_stages = data.get("total_stages", 0)
        stage_name = data.get("stage_name", "")
        self.stage_started.emit(stage_index, total_stages, stage_name)

    def _on_script_confirm_requested(self, data: dict[str, Any]) -> None:
        """Handle PowerShell execution confirmation requests from tools."""
        request_id = data.get("request_id", "")
        command = data.get("command", "")
        self.script_confirm_requested.emit(request_id, command)

    def reset_state(self) -> None:
        """Reset all state for a new task."""
        self._clear_llm_state()
        self._tool_states.clear()
        self._active_tools.clear()

    def _clear_llm_state(self) -> None:
        """Clear transient LLM response state."""
        self._tool_call_buffer.clear()

    # --- Interface Implementation ---
    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    # --- LLM Event Handlers ---
    def on_llm_start(self) -> None:
        self._clear_llm_state()
        self.ai_response_start.emit()

    def on_llm_end(self) -> None:
        self._clear_llm_state()

    def on_llm_chunk(self, chunk: Any) -> None:
        # Handle text content
        if text := self._extract_text(chunk):
            self.new_token_received.emit(text)

        # Handle tool call chunks
        if tc_chunks := getattr(chunk, "tool_call_chunks", None):
            self._process_tool_call_chunks(tc_chunks)

    # --- Tool Event Handlers ---
    def on_tool_start(self, run_id: str, name: str, args: Any) -> None:
        state = {"name": name, "status": "⏳"}
        self._tool_states.append(state)

        if run_id:
            self._active_tools[run_id] = state

        self._emit_tool_execution()

    def on_tool_end(self, run_id: str, name: str, output: Any) -> None:
        status = "✅" if self._is_success(output) else "❌"
        self._finalize_tool(run_id, name, status)

    def on_tool_error(self, run_id: str, name: str, error: Any) -> None:
        self._finalize_tool(run_id, name, "❌")
        error_msg = str(error) if error else "Unknown error occurred."
        self.tool_error_occurred.emit(f"Error in tool '{name}': {error_msg}")

    def on_fatal_error(self, run_id: str, name: str, error: Any) -> None:
        error_msg = str(error) if error else "Unknown fatal error."
        self.fatal_error_occurred.emit(f"Fatal error in '{name}': {error_msg}")

    # --- Internal Logic ---
    def _finalize_tool(self, run_id: str, name: str, status: str) -> None:
        """Update tool status and refresh UI."""
        if run_id and (state := self._active_tools.pop(run_id, None)):
            state["status"] = status
        else:
            # Fallback: Find the last matching tool still running
            for tool in reversed(self._tool_states):
                if tool["name"] == name and tool["status"] == "⏳":
                    tool["status"] = status
                    break
        self._emit_tool_execution()

    def _process_tool_call_chunks(self, tc_chunks: list[dict]) -> None:
        """Accumulate tool chunks and update the plan UI."""
        updated = any(self._update_tool_call_buffer(tc) for tc in tc_chunks)
        if updated:
            self._emit_tool_plan()

    def _update_tool_call_buffer(self, tc: dict) -> bool:
        """Merge a streaming tool chunk into the buffer."""
        idx = tc.get("index", 0)
        entry = self._tool_call_buffer.setdefault(idx, {"name": "", "args": ""})

        changed = False
        if name := tc.get("name"):
            entry["name"] += name
            changed = True
        if args := tc.get("args"):
            entry["args"] += args
            changed = True
        return changed

    def _emit_tool_plan(self) -> None:
        if not self._tool_call_buffer:
            return

        display_calls = []
        for idx in sorted(self._tool_call_buffer):
            entry = self._tool_call_buffer[idx]
            name = entry["name"] or "..."
            formatted_args = self._format_streaming_args(entry["args"])
            display_calls.append(f"### 🛠️ {name}\n{formatted_args}")

        self.tool_plan_updated.emit("\n\n".join(display_calls))

    def _emit_tool_execution(self) -> None:
        lines = [f"[{i+1}] {t['name']} {t['status']}" for i, t in enumerate(self._tool_states)]
        self.tool_execution_updated.emit("\n".join(lines))

    def _format_streaming_args(self, raw_args: str) -> str:
        """Format JSON arguments gracefully handling streaming/incomplete states."""
        if not raw_args:
            return "*(Loading...)*"

        if parsed := self._try_parse_json_args(raw_args):
            return parsed

        return self._parse_partial_json(raw_args)

    def _try_parse_json_args(self, raw_args: str) -> str | None:
        """Attempt to parse arguments as JSON; return None if partial."""
        try:
            args_dict = json.loads(raw_args)
        except json.JSONDecodeError:
            return None

        if isinstance(args_dict, dict) and args_dict:
            return "\n\n".join(f"**{k}**:  {v}" for k, v in args_dict.items())
        return "*(No arguments)*"

    def _parse_partial_json(self, raw_args: str) -> str:
        lines = []
        # Find complete pairs
        matches = self._PARTIAL_JSON_PATTERN.findall(raw_args)
        keys_found = set()

        for key, str_val, other_val in matches:
            value = str_val if str_val else other_val
            lines.append(f"**{key}**:  {value}")
            keys_found.add(key)

        # Find trailing/incomplete key
        if trail_match := self._TRAILING_KEY_PATTERN.search(raw_args):
            key, partial_val = trail_match.groups()
            if key not in keys_found:
                lines.append(f"**{key}**:  {partial_val}▌")

        return "\n\n".join(lines) if lines else f"```\n{raw_args}▌\n```"

    def _extract_text(self, chunk: Any) -> str:
        """Robust text extraction from various chunk formats."""
        if not chunk:
            return ""

        # If chunk has 'content' attribute, use that; otherwise use chunk itself
        content = getattr(chunk, "content", chunk)

        if isinstance(content, str):
            return content

        # Handle list of content blocks (e.g. OpenAI/Anthropic vision)
        if isinstance(content, list):
            parts = []
            for item in content:
                parts.append(item if isinstance(item, str) else item.get("text", ""))
            return "".join(parts)

        return str(content)

    @staticmethod
    def _is_success(output: Any) -> bool:
        """Determine tool execution success."""
        if isinstance(output, str):
            try:
                return parse_tool_response(output)["success"]
            except (ValueError, KeyError, TypeError):
                # Fallback if parsing fails but output exists
                return True
        if isinstance(output, dict):
            return bool(output.get("success", False))
        return False


class QtAgentThread(QThread):
    def __init__(self, task: AgentTask):
        super().__init__()
        self.task = task

    def run(self) -> None:
        self.task.run()

    def cancel(self) -> None:
        """Propagate cancellation to the underlying agent task."""
        self.task.cancel()
