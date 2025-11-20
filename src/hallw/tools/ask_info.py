import queue
import threading
from typing import Optional

from langchain_core.tools import tool
from rich.console import Console

from hallw.tools import build_tool_response
from hallw.utils import config

console = Console()


@tool
def ask_for_more_info(question: str) -> str:
    """
    Call this tool when you need to ask user directly for more information.

    Args:
        question: The question you want to ask about
    """
    if not config.allow_ask_info_tool:
        return build_tool_response(
            False, "User does not accept interactive questions for this task."
        )

    response = get_user_input(timeout=60)

    if response is None:
        return build_tool_response(False, "User did not respond in time (60 seconds).")

    return build_tool_response(
        True, "User provided additional information.", {"response": response}
    )


# Helper function to get user input with timeout
def get_user_input(timeout: int) -> Optional[str]:
    q: queue.Queue[Optional[str]] = queue.Queue()

    def worker():
        try:
            response = console.input("[bold green]Your response: [/bold green]") + " "
            q.put(response)
        except Exception:
            q.put(None)

    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

    try:
        return q.get(timeout=timeout)
    except queue.Empty:
        return None
