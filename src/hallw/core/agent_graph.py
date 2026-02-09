from typing import List

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from hallw.core.agent_renderer import AgentRenderer
from hallw.tools import (
    build_stages,
    build_tool_response,
    dummy_for_missed_tool,
    parse_tool_response,
)
from hallw.utils import config as hallw_config

from .agent_state import AgentState, AgentStats


def build_graph(
    model: ChatOpenAI,
    tools_dict: dict[str, BaseTool],
    checkpointer: BaseCheckpointSaver,
    renderer: AgentRenderer,
) -> StateGraph:
    async def build(state: AgentState, config: RunnableConfig) -> AgentState:
        messages = []
        build_model = model.bind_tools([build_stages], tool_choice="required")
        response = await build_model.ainvoke(state["messages"], config=config)
        messages.append(response)

        # Track stats from build stage
        stats_delta: AgentStats = {
            "input_tokens": 0,
            "output_tokens": 0,
            "tool_call_counts": 1,
            "failures": 0,
            "failures_since_last_reflection": 0,
        }
        if response.usage_metadata:
            stats_delta["input_tokens"] = response.usage_metadata.get("input_tokens", 0)
            stats_delta["output_tokens"] = response.usage_metadata.get("output_tokens", 0)

        tool_calls = response.tool_calls
        if not tool_calls:
            raise ValueError("Build stage expected a tool call but got none.")

        tool_call = tool_calls[0]
        tool_id = tool_call.get("id")
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})

        tool_output = await build_stages.ainvoke(tool_args, config=config)
        tool_output = parse_tool_response(tool_output)

        stage_names: List[str] = tool_output.get("data", {}).get("stage_names", [])
        stage_nums = len(stage_names)

        renderer.on_tool_plan_updated({"plan": stage_names})
        renderer.on_stage_started({"stage_index": 0, "total_stages": stage_nums, "stage_name": stage_names[0]})

        stage_info = (
            f"Current stage (1/{stage_nums}): {stage_names[0]}." " Please complete this stage then proceed to the next."
        )
        combined_content = f"{tool_output}\n\n[System Note]: {stage_info}"

        messages.append(ToolMessage(content=combined_content, tool_call_id=tool_id, name=tool_name))

        return {
            "messages": messages,
            "total_stages": stage_nums,
            "stage_names": stage_names,
            "current_stage": 0,
            "stats": stats_delta,
        }

    async def call_model(state: AgentState, config: RunnableConfig) -> AgentState:
        response = await model.ainvoke(state["messages"], config=config)

        if response is None:
            raise RuntimeError("Model returned no response")

        stats_delta: AgentStats = {
            "input_tokens": 0,
            "output_tokens": 0,
            "tool_call_counts": 0,
            "failures": 0,
            "failures_since_last_reflection": 0,
        }

        empty_response = False

        if response.usage_metadata:
            stats_delta["input_tokens"] = response.usage_metadata.get("input_tokens", 0)
            stats_delta["output_tokens"] = response.usage_metadata.get("output_tokens", 0)

        if not response.content.strip() and not response.tool_calls:
            empty_response = True
            hint_message = HumanMessage(content="System: The previous response was empty. Please continue your task.")
            return {
                "messages": [hint_message],
                "stats": stats_delta,
                "empty_response": empty_response,
            }

        return {
            "messages": [response],
            "stats": stats_delta,
            "empty_response": empty_response,
        }

    async def call_tool(state: AgentState, config: RunnableConfig) -> AgentState:
        ai_message = state["messages"][-1]
        tool_calls = ai_message.tool_calls

        messages: list[ToolMessage] = []

        stats_delta: AgentStats = {
            "tool_call_counts": 0,
            "failures": 0,
            "failures_since_last_reflection": 0,
        }

        current_stage = state.get("current_stage", 0)
        task_completed_update = False

        # 1. Check for tool calls
        if not tool_calls:
            return {
                "messages": [],
                "stats": stats_delta,
            }

        # 2. Execute tool calls
        for tool_call in tool_calls:
            tool_id = tool_call.get("id")
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            tool_obj = tools_dict.get(tool_name)

            # 2.1 Tool not found
            if tool_obj is None:
                tool_obj = dummy_for_missed_tool
                tool_obj.name = tool_name
                tool_args = {"name": tool_name}

            # 2.2 Execute tool
            try:
                # Pass renderer through config's configurable
                tool_config = RunnableConfig(
                    configurable={
                        **config.get("configurable", {}),
                        "renderer": renderer,
                    }
                )
                tool_response = await tool_obj.ainvoke(tool_args, config=tool_config)
            except Exception as e:
                tool_response = build_tool_response(
                    success=False, message=f"Tool {tool_name} execution failed: {str(e)}"
                )

            stats_delta["tool_call_counts"] += 1

            # 2.3 Parse result
            tool_result = parse_tool_response(tool_response)
            success = tool_result.get("success", False)

            if not success:
                stats_delta["failures"] += 1
                stats_delta["failures_since_last_reflection"] += 1

            # Create the basic ToolMessage
            new_tool_message = ToolMessage(content=tool_response, tool_call_id=tool_id, name=tool_name)

            # 2.4 Exam end of stages
            if tool_name == "end_current_stage":
                renderer.on_stage_completed(
                    {
                        "stage_index": current_stage,
                        "total_stages": state.get("total_stages", 0),
                        "stage_name": state["stage_names"][current_stage],
                    },
                )
                current_stage += 1
                if current_stage >= state.get("total_stages", 0):
                    task_completed_update = True
                else:
                    stage_info = (
                        f"Current stage ({current_stage+1}/{state.get('total_stages', 0)}):"
                        f" {state['stage_names'][current_stage]}."
                        " Please complete this stage then proceed to the next."
                    )
                    new_tool_message.content = str(new_tool_message.content) + f"\n\n[System Note]: {stage_info}"

                    renderer.on_stage_started(
                        {
                            "stage_index": current_stage,
                            "total_stages": state.get("total_stages", 0),
                            "stage_name": state["stage_names"][current_stage],
                        },
                    )

            messages.append(new_tool_message)

        return {
            "messages": messages,
            "current_stage": current_stage,
            "task_completed": task_completed_update,
            "stats": stats_delta,
        }

    async def reflection(state: AgentState, config: RunnableConfig) -> AgentState:
        stats = state["stats"]
        current_failures_cycle = stats.get("failures_since_last_reflection", 0)

        # 1. Build hint text
        hint_text = f"""
        System Notification:
        You have accumulated a total of {stats.get('failures', 0)} failures during this task so far.
        The most recent action also failed.

        Please stop and reflect:
        1. Analyze why the previous steps failed.
        2. Adjust your plan to avoid repeating the same mistakes.
        3. Propose the next correct tool calls.
        """
        hint_message = HumanMessage(content=hint_text.strip())
        messages_for_model = state["messages"] + [hint_message]

        # 3. Call model for reflection
        response = await model.ainvoke(messages_for_model, config=config)

        # 4. Prepare Stats update
        stats_delta: AgentStats = {
            "failures_since_last_reflection": -current_failures_cycle,
            "input_tokens": 0,
            "output_tokens": 0,
        }

        if response.usage_metadata:
            stats_delta["input_tokens"] = response.usage_metadata.get("input_tokens", 0)
            stats_delta["output_tokens"] = response.usage_metadata.get("output_tokens", 0)

        if response.content:
            pass

        # 5. Return
        return {"messages": [response], "stats": stats_delta}

    def route_from_model(state: AgentState) -> str:
        # Route to tools if there are actual tool calls
        last_msg = state["messages"][-1]
        if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
            return "tools"

        # Route to model to keep running
        return "model"

    def route_from_tools(state: AgentState) -> str:
        if state["task_completed"]:
            return "end"

        threshold = hallw_config.model_reflection_threshold
        stats = state["stats"]
        failures_cycle = stats.get("failures_since_last_reflection", 0)

        if failures_cycle > 0 and failures_cycle % threshold == 0:
            return "reflection"

        return "model"

    # --- Graph Definition ---

    builder = StateGraph(AgentState)

    builder.add_node("build", build)
    builder.add_node("model", call_model)
    builder.add_node("tools", call_tool)
    builder.add_node("reflection", reflection)

    builder.add_edge(START, "build")
    builder.add_edge("build", "model")

    builder.add_conditional_edges(
        "model",
        route_from_model,
        {
            "model": "model",
            "tools": "tools",
        },
    )

    builder.add_conditional_edges(
        "tools",
        route_from_tools,
        {
            "model": "model",
            "reflection": "reflection",
            "end": END,
        },
    )

    builder.add_edge("reflection", "tools")

    workflow = builder.compile(checkpointer=checkpointer)

    return workflow
