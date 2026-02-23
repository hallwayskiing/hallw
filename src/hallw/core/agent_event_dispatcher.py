import asyncio
from typing import Any, Callable

from hallw.tools import ToolResult, parse_tool_response


class AgentEventDispatcher:
    def __init__(self, renderer: Any):
        self.renderer = renderer
        self._handlers: dict[tuple[str, str | None], Callable] = {}
        self._setup_default_handlers()

    def _setup_default_handlers(self):
        # Task lifecycle
        self.register("on_chain_start", name="LangGraph")(lambda r, ev: r.on_task_started())
        self.register("on_chain_end", name="LangGraph")(lambda r, ev: r.on_task_finished())

        # LLM Events
        self.register("on_chat_model_start")(lambda r, ev: r.on_llm_start())
        self.register("on_chat_model_stream")(self._handle_llm_stream)
        self.register("on_chat_model_end")(lambda r, ev: r.on_llm_end())

        # Tool Events
        self.register("on_tool_start")(self._handle_tool_start)
        self.register("on_tool_end")(self._handle_tool_end)
        self.register("on_tool_error")(self._handle_tool_error)

        # System Events
        self.register("on_fatal_error")(
            lambda r, ev: r.on_fatal_error(ev.get("run_id"), ev.get("name"), ev.get("data", {}).get("error"))
        )

        # Custom Events
        self.register("on_custom_event", name="stages_built")(lambda r, ev: r.on_stages_built(ev.get("data", {})))
        self.register("on_custom_event", name="stage_started")(lambda r, ev: r.on_stage_started(ev.get("data", {})))
        self.register("on_custom_event", name="stages_completed")(
            lambda r, ev: r.on_stages_completed(ev.get("data", {}))
        )
        self.register("on_custom_event", name="stages_edited")(lambda r, ev: r.on_stages_edited(ev.get("data", {})))

    def register(self, event_kind: str, name: str | None = None):
        def decorator(func: Callable):
            self._handlers[(event_kind, name)] = func
            return func

        return decorator

    async def dispatch(self, event: dict[str, Any]):
        kind, name = event.get("event"), event.get("name")
        handler = self._handlers.get((kind, name)) or self._handlers.get((kind, None))
        if handler:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(self.renderer, event)
                else:
                    handler(self.renderer, event)
            except Exception as e:
                self.renderer.on_fatal_error("dispatcher", kind, f"Dispatch error: {e}")

    def _handle_llm_stream(self, renderer, event):
        chunk = event.get("data", {}).get("chunk")
        if chunk:
            renderer.on_llm_chunk(text=self._extract_text(chunk), reasoning=self._extract_reasoning(chunk))

    def _handle_tool_start(self, renderer, event):
        renderer.on_tool_start(event.get("run_id"), event.get("name"), event.get("data", {}).get("input"))

    def _handle_tool_end(self, renderer, event):
        output = event.get("data", {}).get("output")
        parsed = parse_tool_response(output)
        log_msg = self._format_tool_log(event.get("name"), parsed)
        renderer.on_tool_end(event.get("run_id"), event.get("name"), output, parsed.get("success", False), log_msg)

    def _handle_tool_error(self, renderer, event):
        err = event.get("data", {}).get("error")
        renderer.on_tool_error(event.get("run_id"), event.get("name"), str(err))

    def _format_tool_log(self, name: str, parsed: ToolResult) -> str:
        sign = "✅" if parsed.get("success") else "❌"
        msg = parsed.get("message", "")
        summary = (msg[:200] + "...") if len(msg) > 200 else msg
        return f"{sign} Tool {name}: {summary}"

    def _extract_reasoning(self, chunk: Any) -> str:
        if not chunk:
            return ""
        r = (
            getattr(chunk, "reasoning_content", None)
            or (chunk.additional_kwargs.get("reasoning_content") if hasattr(chunk, "additional_kwargs") else None)
            or (chunk.text if hasattr(chunk, "type") and chunk.type == "thought" else "")
        )
        return str(r) if r else ""

    def _extract_text(self, chunk: Any) -> str:
        if not chunk:
            return ""
        content = getattr(chunk, "content", chunk if isinstance(chunk, str) else None)
        if content == "</think>" or content is None:
            return ""
        if isinstance(content, list):
            return "".join([i if isinstance(i, str) else i.get("text", "") for i in content])
        return str(content)
