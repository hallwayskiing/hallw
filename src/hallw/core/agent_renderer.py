from typing import Any, Dict


class AgentRenderer:
    """
    Abstract base class for rendering agent events.
    Responsible for defining the interface and handling common event dispatch logic.
    """

    def start(self) -> None:
        """Start the renderer"""
        raise NotImplementedError

    def stop(self) -> None:
        """Stop the renderer"""
        raise NotImplementedError

    def handle_event(self, event: Dict[str, Any]) -> None:
        """
        General event dispatcher.
        Parse the event type and call the corresponding abstract handler method.
        """
        kind = event.get("event")
        data = event.get("data", {})
        name = event.get("name", "")
        run_id = event.get("run_id", "")

        if kind == "on_chat_model_start":
            self.on_llm_start()
        elif kind == "on_chat_model_stream":
            chunk = data.get("chunk")
            if chunk is not None:
                self.on_llm_chunk(chunk)
        elif kind == "on_chat_model_end":
            self.on_llm_end()
        elif kind == "on_tool_start":
            self.on_tool_start(run_id, name, data.get("input"))
        elif kind == "on_tool_end":
            self.on_tool_end(run_id, name, data.get("output"))
        elif kind == "on_tool_error":
            self.on_tool_error(run_id, name, data.get("error"))
        elif kind == "on_fatal_error":
            self.on_fatal_error(run_id, name, data.get("error"))

    def on_llm_start(self) -> None:
        raise NotImplementedError

    def on_llm_chunk(self, chunk: Any) -> None:
        raise NotImplementedError

    def on_llm_end(self) -> None:
        raise NotImplementedError

    def on_tool_start(self, run_id: str, name: str, args: Any) -> None:
        raise NotImplementedError

    def on_tool_end(self, run_id: str, name: str, output: Any) -> None:
        raise NotImplementedError

    def on_tool_error(self, run_id: str, name: str, error: Any) -> None:
        raise NotImplementedError

    def on_fatal_error(self, run_id: str, name: str, error: Any) -> None:
        raise NotImplementedError
