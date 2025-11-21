import asyncio
import sys
import uuid
import warnings

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from rich.align import Align
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from typer import Argument, Typer

from hallw import AgentState, run_task
from hallw.tools import load_tools
from hallw.ui.renderer import AgentRenderer
from hallw.utils import config, generatePrompt, logger

warnings.filterwarnings(
    "ignore", message=".*LangSmith now uses UUID v7.*"
)  # Ignore UUID v7 warning since it's triggered by libraries

# Shut down the annoying RuntimeError on Windows event loop shutdown
if sys.platform.startswith("win"):
    from asyncio.proactor_events import _ProactorBasePipeTransport

    def silence_event_loop_closed(self):
        pass

    _ProactorBasePipeTransport.__del__ = silence_event_loop_closed  # type: ignore

app = Typer()
console = Console()


@app.command()
def main(user_task: str = Argument(None, help="Describe a task")) -> None:
    console.print(Panel(Align.center("🤖 Welcome to HALLW"), style="bold blue"))

    if not config.model_api_key or not config.model_api_key.get_secret_value():
        console.print("[red]❌ Model API key is not set! Please set it in the .env file.[/red]")
        return

    if not user_task:
        user_task = console.input("[bold green]Describe a task: [/bold green] ")

    if not user_task:
        console.print("[red]❌ Task cannot be empty![/red]")
        return

    tools_dict = load_tools()

    llm = ChatOpenAI(
        model=config.model_name,
        base_url=config.model_endpoint,
        api_key=config.model_api_key.get_secret_value(),
        temperature=config.model_temperature,
        max_tokens=config.model_max_output_tokens,
        streaming=True,
        stream_usage=True,
    ).bind_tools(list(tools_dict.values()), tool_choice="auto")

    renderer = AgentRenderer()
    renderer.start()

    task_id = str(uuid.uuid4())

    initial_state: AgentState = {
        "messages": [
            SystemMessage(content=generatePrompt(user_task, tools_dict)),
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
            "input_tokens": 0,
            "output_tokens": 0,
            "failures": 0,
            "failures_since_last_reflection": 0,
        },
    }

    hello_message = f"Model: {config.model_name}\nTask: {user_task}\nTask ID: {task_id}"
    logger.info(hello_message)
    console.print(Panel((hello_message), style="bold white"))

    try:
        asyncio.run(run_task(task_id, llm, tools_dict, renderer, initial_state))
    except KeyboardInterrupt:
        logger.warning("Interrupted by user.")
        console.print(Panel("Interrupted by user.", title="Warning", style="red"))
    except Exception as e:
        logger.error(f"A fatal error occurs: {e}", exc_info=True)
        console.print(Panel(Markdown(f"{e}"), title="Fatal Error", style="red"))
    finally:
        stats = initial_state["stats"]
        statistics = "Statistics:\n"
        for key, value in stats.items():
            statistics += f"  - {key}: {value}\n"
        logger.info(statistics)
        console.print(Panel(Markdown(statistics), title="Task Statistics", style="bold white"))
        console.print(Panel(Align.center("🤖 Thank you for using HALLW"), style="bold blue"))
        console.print("\n\n")
        renderer.stop()


if __name__ == "__main__":
    app()
