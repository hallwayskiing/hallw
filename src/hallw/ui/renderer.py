from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel


class AgentRenderer:
    """Render LangGraph events using Rich panels."""

    def __init__(self, console: Optional[Console] = None) -> None:
        self.console = console or Console()
        self.live: Optional[Live] = None
        self.current_response: Optional[Dict[str, Any]] = None
        self.active_tools: List[Dict[str, Any]] = []

        # Buffer to cache streaming tool call fragments: {index: {name: "...", args: "..."}}
        self._tool_call_buffer: Dict[int, Dict[str, str]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def start(self) -> None:
        """Start the live display."""
        if self.live is None:
            self.live = Live(
                self._render(),
                console=self.console,
                refresh_per_second=12,
                transient=True,
                vertical_overflow="visible",
            )
            self.live.start()

    def stop(self) -> None:
        """Stop the live display."""
        if self.live:
            self.live.stop()
            self.live = None

    def handle_event(self, event: Dict[str, Any]) -> None:
        """Dispatch events to their respective handlers."""
        kind = event.get("event")
        data = event.get("data", {})
        name = event.get("name", "")

        if kind == "on_chat_model_start":
            self.on_llm_start()
        elif kind == "on_chat_model_stream":
            chunk = data.get("chunk")
            if chunk is not None:
                self.on_llm_chunk(chunk)
        elif kind == "on_tool_start":
            self.on_tool_start(name=name, args=data.get("input"))
        elif kind == "on_tool_end":
            self.on_tool_end(name=name, output=data.get("output"))

    # ------------------------------------------------------------------
    # Event helpers
    # ------------------------------------------------------------------
    def on_llm_start(self) -> None:
        """Handle the start of an LLM generation."""
        self.current_response = {"text": "", "tool_calls": []}
        self._tool_call_buffer = {}  # Clear tool call buffer
        self.start()  # Ensure live is running
        self.refresh()

    def on_llm_chunk(self, chunk: Any) -> None:
        """Handle streaming chunks from the LLM."""
        if not self.current_response:
            self.current_response = {"text": "", "tool_calls": []}

        # 1. Handle text stream
        self.current_response["text"] += self._extract_text(chunk)

        # 2. Handle tool call stream (tool_call_chunks)
        # LangChain/OpenAI stream args in fragments, so we must accumulate them.
        tc_chunks = getattr(chunk, "tool_call_chunks", [])
        if tc_chunks:
            for tc in tc_chunks:
                idx = tc.get("index", 0)

                # Initialize buffer for this index
                if idx not in self._tool_call_buffer:
                    self._tool_call_buffer[idx] = {"name": "", "args": ""}

                # Accumulate name (usually only in the first chunk)
                if tc.get("name"):
                    self._tool_call_buffer[idx]["name"] += tc["name"]

                # Accumulate args (character-level concatenation)
                if tc.get("args"):
                    self._tool_call_buffer[idx]["args"] += tc["args"]

            # Format buffer content and update current response
            display_calls = []
            for idx in sorted(self._tool_call_buffer.keys()):
                entry = self._tool_call_buffer[idx]
                name = entry["name"] or "unknown"
                raw_args = entry["args"]

                # Attempt to prettify JSON args if possible
                formatted_args = raw_args
                try:
                    if raw_args.strip().endswith("}"):
                        parsed = json.loads(raw_args)
                        formatted_args = json.dumps(parsed, ensure_ascii=False)
                except json.JSONDecodeError:
                    # JSON is likely incomplete during streaming; show raw string
                    pass

                display_calls.append(f"{name}: {formatted_args}")

            self.current_response["tool_calls"] = display_calls

        self.refresh()

    def on_tool_start(self, name: str, args: Any) -> None:
        """Handle the start of a tool execution."""
        # 1. If we were streaming an LLM response, finish it and print cleanly.
        if self.current_response:
            self.stop()
            self._print_response(self.current_response)
            self.current_response = None
            self._tool_call_buffer = {}

        # 2. Add to active tools list
        self.active_tools.append(
            {
                "name": name or "unknown",
                "status": "⏳",
                "output": None,
            }
        )

        # 3. [CRITICAL] For interactive tools, do NOT start Live mode.
        # We must keep Live stopped to allow `console.input()` to work without conflict.
        if name == "ask_for_more_info":
            self.stop()
            return

        # For normal tools, start Live to show the spinner.
        self.start()
        self.refresh()

    def on_tool_end(self, name: str, output: Any) -> None:
        """Handle the completion of a tool execution."""
        status = "✅" if self._is_success(output) else "❌"

        # Find and remove from active tools
        found_tool = None
        for i, tool in enumerate(self.active_tools):
            if tool["name"] == name:
                found_tool = tool
                del self.active_tools[i]
                break

        if found_tool:
            found_tool["status"] = status
            found_tool["output"] = output

            # Stop live to print the result permanently.
            # This ensures the finished tool is printed as a static block.
            self.stop()
            self._print_tool(found_tool)

            # Restart live only if other background tools are still running.
            if self.active_tools:
                self.start()
                self.refresh()

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    def refresh(self) -> None:
        """Update the live display if active."""
        if self.live:
            self.live.update(self._render())

    def _render(self) -> Group:
        """Compose the visual elements for the Live display."""
        renderables: List[Panel] = []

        # 1. Current streaming LLM response
        if self.current_response:
            renderables.append(self._content_panel(self.current_response))
            if self.current_response["tool_calls"]:
                renderables.append(self._tool_panel(self.current_response))

        # 2. Active tools (Spinners)
        for tool in self.active_tools:
            renderables.append(self._tool_status_panel(tool))

        # Show a placeholder if nothing is rendering to keep Live active
        if not renderables:
            renderables.append(Panel("...", title="🤖 HALLW", border_style="blue"))

        return Group(*renderables)

    def _print_response(self, response: Dict[str, Any]) -> None:
        self.console.print(self._content_panel(response))
        if response["tool_calls"]:
            self.console.print(self._tool_panel(response))

    def _print_tool(self, tool_data: Dict[str, Any]) -> None:
        self.console.print(self._tool_status_panel(tool_data))

    def _content_panel(self, response: Dict[str, Any]) -> Panel:
        # Hide internal XML tags (e.g., <thought>) if present
        text = response["text"]
        end_idx = text.find("<")

        if end_idx != -1:
            content = text[:end_idx]
        else:
            content = text

        # Clean up formatting
        content = content.strip().replace("\n", "") or "Thinking..."

        markdown = Markdown(content, style="bold blue")
        return Panel(markdown, title="🤖 HALLW", border_style="bold blue")

    def _tool_panel(self, response: Dict[str, Any]) -> Panel:
        calls = response["tool_calls"]
        body = "\n".join(calls)
        markdown = Markdown(body, style="bold yellow")
        return Panel(markdown, title="⚡ Tool Plan", border_style="bold yellow")

    def _tool_status_panel(self, log: Dict[str, Any]) -> Panel:
        status_line = f"{log['name']} {log['status']}"
        markdown = Markdown(status_line, style="cyan")
        return Panel(markdown, title="🔧 Tool Execution", border_style="cyan")

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def _extract_text(self, chunk: Any) -> str:
        if chunk is None:
            return ""
        content = getattr(chunk, "content", chunk)
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    parts.append(item.get("text", ""))
                else:
                    parts.append(getattr(item, "text", ""))
            return "".join(parts)
        return str(content)

    def _is_success(self, output: Any) -> bool:
        payload = None
        if isinstance(output, str):
            try:
                payload = json.loads(output)
            except json.JSONDecodeError:
                pass
        elif isinstance(output, dict):
            payload = output

        if isinstance(payload, dict):
            return bool(payload.get("success", True))

        return "true" in str(output).lower()

    def _short_text(self, value: Any, limit: int = 120) -> str:
        if isinstance(value, (dict, list)):
            text = json.dumps(value, ensure_ascii=False)
        else:
            text = str(value)
        return text if len(text) <= limit else f"{text[:limit]}..."

    def _get_value(self, obj: Any, key: str, default: Any = None) -> Any:
        if hasattr(obj, key):
            return getattr(obj, key)
        if isinstance(obj, dict):
            return obj.get(key, default)
        if hasattr(obj, "__dict__") and key in obj.__dict__:
            return obj.__dict__[key]
        return default
