import asyncio
import uuid

import typer
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.panel import Panel

from hallw import AgentState, build_graph, tools_dict
from hallw.tools.playwright.playwright_mgr import browser_close
from hallw.utils import config, generatePrompt, logger

llm = ChatOpenAI(
    model=config.model_name,
    base_url=config.model_endpoint,
    api_key=config.model_api_key.get_secret_value(),
    temperature=config.model_temperature,
    max_tokens=config.model_max_output_tokens,
).bind_tools(list(tools_dict.values()), tool_choice="auto")


async def run_task(user_task: str):
    task_id = uuid.uuid4()
    logger.info(f"Model: {config.model_name}")
    logger.info(f"Task: {user_task}")
    logger.info(f"Task ID: {task_id}")

    workflow, checkpointer = build_graph(llm, tools_dict)

    initial_state: AgentState = {
        "messages": [
            SystemMessage(content=generatePrompt(user_task)),
            HumanMessage(
                content=f"Think step-by-step, plan your actions, and use proper tools to complete the task: {user_task}",
            ),
        ],
        "task_completed": False,
        "stats": {
            "tool_call_counts": 0,
            "failures": 0,
            "input_tokens": 0,
            "output_tokens": 0,
        },
    }

    try:
        logger.info("=" * 30)
        logger.info("Task Start")
        logger.info("=" * 30)

        final_state = await workflow.ainvoke(
            initial_state,
            config={"recursion_limit": 100, "configurable": {"thread_id": task_id}},
        )

        logger.info("Task has been completed successfully.")

    except KeyboardInterrupt:
        logger.warning("Interrupted by user.")
    except Exception as e:
        logger.error(f"A fatal error occurs: {e}")
    finally:
        logger.info("=" * 30)
        logger.info("Statistics:")
        stats = initial_state["stats"]
        for key, value in stats.items():
            logger.info(f"  - {key}: {value}")
        logger.info("=" * 30)
        await browser_close()


app = typer.Typer()
console = Console()


@app.command()
def main(user_task: str = typer.Argument(None, help="Describe a task")):
    console.print(Panel.fit("🤖 Welcome to HALLW", style="bold blue"))

    if not user_task:
        user_task = console.input("[bold green]Describe a task: [/bold green] ")

    if not user_task:
        console.print("[red]❌ Task cannot be empty![/red]")
        return

    if not config.model_api_key:
        console.print("[red]⚠️ API_KEY not detected, please check the .env file[/red]")
        return

    console.print(f"[dim]Starting task: {user_task}...[/dim]")
    asyncio.run(run_task(user_task))

    console.print(Panel.fit("🤖 Thank you for using HALLW", style="bold blue"))


if __name__ == "__main__":
    app()
