"""
Global event bus for cross-module communication.

This module provides a simple pub/sub mechanism for decoupling
tools from UI components. Tools can emit events without knowing
about the UI implementation.

Usage:
    # In a tool (e.g., search.py):
    from hallw.utils import event_bus
    event_bus.emit("captcha_detected", {"engine": "google", "page_index": 0})

    # In UI (e.g., qt_renderer.py):
    from hallw.utils import event_bus
    event_bus.subscribe("captcha_detected", self._on_captcha_detected)
"""

from typing import Any, Callable, Dict, List

# Type alias for event handlers
EventHandler = Callable[[Dict[str, Any]], None]


class EventBus:
    """Simple publish/subscribe event bus for cross-module communication."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[EventHandler]] = {}

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """Subscribe a handler to an event.

        Args:
            event_name: Name of the event to subscribe to
            handler: Callback function that receives event data dict
        """
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        if handler not in self._subscribers[event_name]:
            self._subscribers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        """Unsubscribe a handler from an event.

        Args:
            event_name: Name of the event to unsubscribe from
            handler: The handler function to remove
        """
        if event_name in self._subscribers:
            try:
                self._subscribers[event_name].remove(handler)
            except ValueError:
                pass  # Handler not found, ignore

    def emit(self, event_name: str, data: Dict[str, Any] | None = None) -> None:
        """Emit an event to all subscribers.

        Args:
            event_name: Name of the event to emit
            data: Optional data dict to pass to handlers
        """
        if event_name in self._subscribers:
            event_data = data or {}
            for handler in self._subscribers[event_name]:
                try:
                    handler(event_data)
                except Exception:
                    # Don't let one handler's failure affect others
                    pass

    def clear(self, event_name: str | None = None) -> None:
        """Clear subscribers for an event or all events.

        Args:
            event_name: Specific event to clear, or None to clear all
        """
        if event_name is None:
            self._subscribers.clear()
        elif event_name in self._subscribers:
            self._subscribers[event_name].clear()


# Global singleton instance
_bus = EventBus()

# Module-level convenience functions
subscribe = _bus.subscribe
unsubscribe = _bus.unsubscribe
emit = _bus.emit
clear = _bus.clear


# Event name constants for type safety
class Events:
    """Standard event names used throughout the application."""

    CAPTCHA_DETECTED = "captcha_detected"
    CAPTCHA_RESOLVED = "captcha_resolved"
    STAGE_STARTED = "stage_started"
    SCRIPT_CONFIRM_REQUESTED = "script_confirm_requested"
    SCRIPT_CONFIRM_RESPONDED = "script_confirm_responded"
    TOOL_PLAN_UPDATED = "tool_plan_updated"
