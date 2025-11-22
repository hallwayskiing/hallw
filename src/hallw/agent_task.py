from typing import Dict

from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import BaseCheckpointSaver

from hallw import AgentState, build_graph
from hallw.ui.renderer import AgentRenderer


async def run_task(
    task_id: str,
    llm: ChatOpenAI,
    tools_dict: Dict[str, BaseTool],
    renderer: AgentRenderer,
    initial_state: AgentState,
    checkpointer: BaseCheckpointSaver,
) -> None:
    workflow = build_graph(llm, tools_dict, checkpointer)

    invocation_config = {"recursion_limit": 200, "configurable": {"thread_id": task_id}}

    async for event in workflow.astream_events(
        initial_state,
        config=invocation_config,
        version="v2",
    ):
        renderer.handle_event(event)
