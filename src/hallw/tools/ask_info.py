from langchain_core.tools import tool
from rich.console import Console
from rich.panel import Panel

from hallw.tools import build_tool_response


@tool
def ask_for_more_info(question: str) -> str:
    """
    Call this tool when you need to ask user directly for more information.

    Args:
        question: The question you want to ask about
    """
    console = Console()
    console.print(
        Panel.fit(f"HALLW asking: {question}", title="More Information Needed", border_style="blue")
    )
    response = console.input("[bold green]Your response: [/bold green]")
    return build_tool_response(
        True, "User provided additional information.", {"response": response}
    )
