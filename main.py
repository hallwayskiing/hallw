import asyncio
import uuid
import warnings

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from rich.align import Align
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from typer import Argument, Typer

from hallw import AgentState, build_graph
from hallw.tools import load_tools
from hallw.ui.renderer import AgentRenderer
from hallw.utils import config, generatePrompt, logger

warnings.filterwarnings(
    "ignore", message=".*LangSmith now uses UUID v7.*"
)  # Ignore UUID v7 warning since it's triggered by libraries


app = Typer()
console = Console()


async def run_task(user_task: str) -> None:
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

    task_id = uuid.uuid4()

    hello_message = f"Model: {config.model_name}\nTask: {user_task}\nTask ID: {task_id}"
    logger.info(hello_message)
    console.print(Panel((hello_message), style="bold white"))

    workflow, _ = build_graph(llm, tools_dict)

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
    except Exception as e:
        logger.error("A fatal error occurs", exc_info=True)
        console.print(Panel(f"{e}", title="Fatal Error", style="red"))
    finally:
        renderer.stop()
        stats = initial_state["stats"]
        statistics = "Statistics:\n"
        for key, value in stats.items():
            statistics += f"  - {key}: {value}\n"
        logger.info(statistics)
        console.print(Panel(Markdown(statistics), title="Task Statistics", style="bold white"))


@app.command()
def main(user_task: str = Argument(None, help="Describe a task")) -> None:
    console.print(Panel(Align.center("🤖 Welcome to HALLW"), style="bold blue"))

    if not user_task:
        user_task = console.input("[bold green]Describe a task: [/bold green] ")

    if not user_task:
        console.print("[red]❌ Task cannot be empty![/red]")
        return

    asyncio.run(run_task(user_task))

    console.print(Panel(Align.center("🤖 Thank you for using HALLW"), style="bold blue"))


if __name__ == "__main__":
    app()
