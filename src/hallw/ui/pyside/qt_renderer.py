import json
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, QThread, Signal

from hallw.core import AgentRenderer, AgentTask
from hallw.tools import parse_tool_response
from hallw.utils import config


class QtAgentRenderer(QObject, AgentRenderer):
    new_token_received = Signal(str)
    tool_plan_updated = Signal(str)
    tool_execution_updated = Signal(str)
    request_input = Signal(str)
    task_finished = Signal()
    ai_response_start = Signal()
    tool_error_occurred = Signal(str)
    fatal_error_occurred = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        AgentRenderer.__init__(self)

        self.current_response: Optional[Dict[str, Any]] = None
        self._tool_call_buffer: Dict[int, Dict[str, str]] = {}

        self.tool_states: List[Dict[str, Any]] = []
        self._active_tools: Dict[str, Dict[str, Any]] = {}

    def reset_state(self):
        self.tool_states.clear()
        self._active_tools.clear()
        self.tool_execution_updated.emit("")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def on_llm_start(self) -> None:
        self.current_response = {"text": "", "tool_calls": []}
        self._tool_call_buffer = {}
        self.ai_response_start.emit()

    def on_llm_end(self) -> None:
        self.current_response = None
        self._tool_call_buffer = {}

    def on_llm_chunk(self, chunk: Any) -> None:
        if not self.current_response:
            self.current_response = {"text": "", "tool_calls": []}

        # 1. Process text chunks
        text = self._extract_text(chunk)
        if text:
            self.current_response["text"] += text
            self.new_token_received.emit(text)

        # 2. Process tool call chunks
        tc_chunks = getattr(chunk, "tool_call_chunks", [])
        if tc_chunks:
            self._process_tool_call_chunks(tc_chunks)

    def on_tool_start(self, run_id: str, name: str, args: Any) -> None:
        # Create state object
        state = {"name": name, "status": "⏳"}

        # Append to list (for ordered display)
        self.tool_states.append(state)
        # Store in mapping (for quick lookup and update)
        if run_id:
            self._active_tools[run_id] = state

        self._emit_tool_execution()

        # Handle special tool requests
        if name == "ask_for_more_info" and config.allow_ask_info_tool:
            question = "Agent needs input."
            if isinstance(args, str):
                try:
                    j = json.loads(args)
                    if isinstance(j, dict):
                        question = j.get("question", question)
                except Exception:
                    pass
            elif isinstance(args, dict):
                question = args.get("question", question)
            self.request_input.emit(question)

    def on_tool_end(self, run_id: str, name: str, output: Any) -> None:
        status = "✅" if self._is_success(output) else "❌"

        # Use run_id to find
        if run_id and run_id in self._active_tools:
            self._active_tools[run_id]["status"] = status
            del self._active_tools[run_id]  # Remove active state
        else:
            # Fallback: reverse search
            for tool in reversed(self.tool_states):
                if tool["name"] == name and tool["status"] == "⏳":
                    tool["status"] = status
                    break

        self._emit_tool_execution()

    def on_tool_error(self, run_id: str, name: str, error: Any) -> None:
        # Mark tool as failed
        if run_id and run_id in self._active_tools:
            self._active_tools[run_id]["status"] = "❌"
            del self._active_tools[run_id]
        else:
            for tool in reversed(self.tool_states):
                if tool["name"] == name and tool["status"] == "⏳":
                    tool["status"] = "❌"
                    break

        self._emit_tool_execution()

        # Emit error message
        error_msg = (
            str(error) if error is not None else "Unknown error occurred during tool execution."
        )
        self.tool_error_occurred.emit(f"Error in tool '{name}': {error_msg}")

    def on_fatal_error(self, run_id: str, name: str, error: Any) -> None:
        error_msg = str(error) if error is not None else "Unknown fatal error occurred."
        self.fatal_error_occurred.emit(f"Fatal error in '{name}': {error_msg}")

    def _process_tool_call_chunks(self, tc_chunks: List[Dict]):
        """Process streaming tool call chunks and update UI"""
        for tc in tc_chunks:
            idx = tc.get("index", 0)
            if idx not in self._tool_call_buffer:
                self._tool_call_buffer[idx] = {"name": "", "args": ""}

            if tc.get("name"):
                self._tool_call_buffer[idx]["name"] += tc["name"]
            if tc.get("args"):
                self._tool_call_buffer[idx]["args"] += tc["args"]

        # Format and send to frontend
        display_calls = []
        for idx in sorted(self._tool_call_buffer.keys()):
            entry = self._tool_call_buffer[idx]
            name = entry["name"] or "unknown"
            raw_args = entry["args"]
            formatted_args = self._format_json_args(raw_args)
            display_calls.append(f"### 🛠️ {name}\n{formatted_args}")

        self.tool_plan_updated.emit("\n\n".join(display_calls))

    def _format_json_args(self, raw_args: str) -> str:
        """Format JSON arguments for display"""
        try:
            args_dict = json.loads(raw_args)
            if isinstance(args_dict, dict) and args_dict:
                lines = []
                for key, value in args_dict.items():
                    val_str = str(value) if not isinstance(value, str) else value
                    lines.append(f"**{key}**:  {val_str}")
                return "\n".join(lines)
            elif isinstance(args_dict, dict) and not args_dict:
                return "*(No arguments)*"
        except json.JSONDecodeError:
            pass
        return f"```json\n{raw_args}\n```"

    def _emit_tool_execution(self):
        """Emit the current tool execution status to the frontend"""
        lines = [f"[{i+1}] {t['name']} {t['status']}" for i, t in enumerate(self.tool_states)]
        self.tool_execution_updated.emit("\n".join(lines))

    def _extract_text(self, chunk: Any) -> str:
        """Extract text content from a chunk"""
        if chunk is None:
            return ""
        content = getattr(chunk, "content", chunk)
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = [item if isinstance(item, str) else item.get("text", "") for item in content]
            return "".join(parts)
        return str(content)

    def _is_success(self, output: Any) -> bool:
        """Determine if the tool execution was successful"""
        if isinstance(output, str):
            return parse_tool_response(output)["success"]
        if isinstance(output, dict):
            return bool(output.get("success", False))
        return False


class QtAgentThread(QThread):
    def __init__(self, task: AgentTask):
        super().__init__()
        self.task = task

    def run(self):
        self.task.run()
