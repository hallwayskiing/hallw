from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from hallw.core import AgentRenderer
from hallw.tools.tool_response import parse_tool_response


class RichAgentRenderer(AgentRenderer):
    """Render LangGraph events using Rich panels."""

    def __init__(self, console: Optional[Console] = None) -> None:
        self.console = console or Console()
        self.live: Optional[Live] = None
        self.current_response: Optional[Dict[str, Any]] = None
        self.active_tools: List[Dict[str, Any]] = []

        # Buffer to cache streaming tool call fragments: {index: {name: "...", args: "..."}}
        self._tool_call_buffer: Dict[int, Dict[str, str]] = {}

    # ------------------------------------------------------------------
    # Protocol for Rich Live
    # ------------------------------------------------------------------
    def __rich__(self) -> Group:
        return self._render()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def start(self) -> None:
        """Start the live display."""
        if self.live is None:
            self.live = Live(
                self,
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

    # ------------------------------------------------------------------
    # Event helpers
    # ------------------------------------------------------------------
    def on_llm_start(self) -> None:
        """Handle the start of an LLM generation."""
        self.current_response = {"text": "Thinking...", "tool_calls": []}
        self._tool_call_buffer = {}  # Clear tool call buffer
        self.start()  # Ensure live is running

    def on_llm_end(self) -> None:
        """Handle the end of LLM generation."""
        if self.current_response and not self.current_response["tool_calls"]:
            self.stop()
            self._print_response(self.current_response)
            self.console.print(self._tool_panel({"tool_calls": ["No tool call in this response."]}))
            self.current_response = None
            self._tool_call_buffer = {}

    def on_llm_chunk(self, chunk: Any) -> None:
        """Handle streaming chunks from the LLM."""
        if not self.current_response:
            self.current_response = {"text": "", "tool_calls": []}

        if self.current_response["text"] == "Thinking...":
            self.current_response["text"] = ""

        # 1. Handle text stream
        self.current_response["text"] += self._extract_text(chunk)

        # 2. Handle tool call stream (tool_call_chunks)
        tc_chunks = getattr(chunk, "tool_call_chunks", [])
        if tc_chunks:
            for tc in tc_chunks:
                idx = tc.get("index", 0)

                if idx not in self._tool_call_buffer:
                    self._tool_call_buffer[idx] = {"name": "", "args": ""}

                if tc.get("name"):
                    self._tool_call_buffer[idx]["name"] += tc["name"]

                if tc.get("args"):
                    self._tool_call_buffer[idx]["args"] += tc["args"]

            # Format buffer content and update current response
            display_calls = []
            for idx in sorted(self._tool_call_buffer.keys()):
                entry = self._tool_call_buffer[idx]
                name = entry["name"] or "unknown"
                raw_args = entry["args"]

                formatted_args = raw_args
                try:
                    if raw_args.strip().endswith("}"):
                        parsed = json.loads(raw_args)
                        formatted_args = json.dumps(parsed, ensure_ascii=False)
                except json.JSONDecodeError:
                    pass

                display_calls.append(f"{name}: {formatted_args}")

            self.current_response["tool_calls"] = display_calls

    def on_tool_start(self, run_id: str, name: str, args: Any) -> None:
        """Handle the start of a tool execution."""
        # 1. If we were streaming an LLM response (with tool calls), finish it.
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

        # 3. For interactive tools, stop Live to allow input.
        if name == "ask_for_more_info":
            self.stop()
            return

        # For normal tools, ensure Live is active.
        self.start()
        self._refresh()

    def on_tool_end(self, run_id: str, name: str, output: Any) -> None:
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
            self.stop()
            self._print_tool(found_tool)

            # Restart live only if other background tools are still running.
            if self.active_tools:
                self.start()
                self._refresh()

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    def _refresh(self) -> None:
        """Update the live display manually (use sparingly)."""
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
            renderables.append(Panel("Thinking...", title="🤖 HALLW", border_style="blue"))

        return Group(*renderables)

    def _print_response(self, response: Dict[str, Any]) -> None:
        self.console.print(self._content_panel(response))
        if response["tool_calls"]:
            self.console.print(self._tool_panel(response))

    def _print_tool(self, tool_data: Dict[str, Any]) -> None:
        self.console.print(self._tool_status_panel(tool_data))

    def _content_panel(self, response: Dict[str, Any]) -> Panel:
        markdown = Markdown(response["text"].strip(), style="bold blue")
        return Panel(markdown, title="🤖 HALLW", border_style="bold blue")

    def _tool_panel(self, response: Dict[str, Any]) -> Panel:
        calls = response["tool_calls"]
        body = "\n".join(calls)
        markdown = Markdown(body.strip(), style="bold yellow")
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
        if isinstance(output, str):
            result = parse_tool_response(output)
            return result["success"]

        if isinstance(output, dict):
            return bool(output.get("success", False))

        return False
