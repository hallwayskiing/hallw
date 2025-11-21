import asyncio
import logging
import warnings

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langsmith import uuid7
from rich.align import Align
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from typer import Argument, Typer

from hallw import AgentState, build_graph, tools_dict
from hallw.tools.playwright.playwright_mgr import browser_close
from hallw.ui.renderer import AgentRenderer
from hallw.utils import config, generatePrompt, logger

warnings.filterwarnings(
    "ignore", message=".*LangSmith now uses UUID v7.*"
)  # Ignore UUID v7 warning since it's triggered by libraries

# Disable noisy third-party loggers at the CLI entry point
logging.getLogger("httpx").disabled = True
logging.getLogger("langchain_core.callbacks.manager").disabled = True

llm = ChatOpenAI(
    model=config.model_name,
    base_url=config.model_endpoint,
    api_key=config.model_api_key.get_secret_value(),
    temperature=config.model_temperature,
    max_tokens=config.model_max_output_tokens,
    streaming=True,
    stream_usage=True,
)

app = Typer()
console = Console()


def _select_tools_for_task(user_task: str) -> dict[str, BaseTool]:
    """Filter tools based on config settings.

    Args:
        user_task: The user's task description (for future expansion)

    Returns:
        Filtered dictionary of tools
    """
    selected = {}

    for tool_name, tool_obj in tools_dict.items():
        # Filter browser tools
        if tool_name.startswith("browser_") and not config.enable_browser_tools:
            continue

        # Filter file tools
        if tool_name.startswith("file_") or tool_name == "get_local_file_list":
            if not config.enable_file_tools:
                continue

        # Filter ask_for_more_info based on config
        if tool_name == "ask_for_more_info" and not config.allow_ask_info_tool:
            continue

        selected[tool_name] = tool_obj

    return selected


async def run_task(user_task: str) -> None:
    task_id = uuid7()
    hello_message = f"Model: {config.model_name}\nTask: {user_task}\nTask ID: {task_id}"
    logger.info(hello_message)
    console.print(Panel((hello_message), style="bold white"))

    # Select tools based on config
    selected_tools = _select_tools_for_task(user_task)
    model_with_tools = llm.bind_tools(list(selected_tools.values()), tool_choice="auto")

    workflow, _ = build_graph(model_with_tools, selected_tools)

    initial_state: AgentState = {
        "messages": [
            SystemMessage(content=generatePrompt(user_task)),
            HumanMessage(
                content=(
                    "Think step-by-step, plan your actions, and use proper tools to "
                    f"complete the task: {user_task}"
                ),
            ),
        ],
        "task_completed": False,
        "stats": {
            "tool_call_counts": 0,
            "failures": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "reflections": 0,
        },
    }

    renderer = AgentRenderer()
    invocation_config = {"recursion_limit": 100, "configurable": {"thread_id": task_id}}

    try:
        renderer.start()

        async for event in workflow.astream_events(
            initial_state,
            config=invocation_config,
            version="v2",
        ):
            renderer.handle_event(event)

    except KeyboardInterrupt:
        logger.warning("Interrupted by user.")
        console.print(Panel("Interrupted by user.", title="Warning", style="red"))
    except Exception as exc:  # pylint: disable=broad-except
        logger.error(f"A fatal error occurs: {exc}")
        console.print(Panel(f"{exc}", title="Fatal Error", style="red"))
    finally:
        renderer.stop()
        stats = initial_state["stats"]
        statistics = "Statistics:\n"
        for key, value in stats.items():
            statistics += f"  - {key}: {value}\n"
        logger.info(statistics)
        console.print(Panel(Markdown(statistics), title="Task Statistics", style="bold white"))
        await browser_close()


@app.command()
def main(user_task: str = Argument(None, help="Describe a task")) -> None:
    console.print(Panel(Align.center("🤖 Welcome to HALLW"), style="bold blue"))

    if not user_task:
        user_task = console.input("[bold green]Describe a task: [/bold green] ")

    if not user_task:
        console.print("[red]❌ Task cannot be empty![/red]")
        return

    if not config.model_api_key:
        console.print("[red]⚠️ API_KEY not detected, please check the .env file[/red]")
        return

    asyncio.run(run_task(user_task))

    console.print(Panel(Align.center("🤖 Thank you for using HALLW"), style="bold blue"))


if __name__ == "__main__":
    app()
