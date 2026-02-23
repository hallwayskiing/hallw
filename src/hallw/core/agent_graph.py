from langchain_core.callbacks.manager import dispatch_custom_event
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from hallw.core import AgentStats
from hallw.tools import (
    build_stages,
    build_tool_response,
    dummy_for_missed_tool,
    edit_stages,
    end_current_stage,
    load_tools,
    parse_tool_response,
)
from hallw.utils import config as app_config
from hallw.utils import get_system_prompt

from .agent_state import AgentState


def build_graph(model, checkpointer) -> StateGraph[AgentState]:
    """
    Builds the LangGraph workflow
    """

    tools_dict = load_tools()
    system_prompt = get_system_prompt()

    # --- Nodes ---

    async def build_node(state: AgentState, config: RunnableConfig):
        append_prompt = """
            Now build the stages for the user request.
            <rules>
            1. You MUST call the `build_stages` tool exactly once.
            2. The `stages` list you provide must be clear, actionable, and in the correct order.
            3. Do NOT call any other tools. Only call `build_stages`.
            4. If the user request is simple, create only one stage to finish it quickly.
            </rules>
        """
        system_msg = SystemMessage(content=f"{system_prompt}\n\n{append_prompt}")

        response = await model.bind_tools([build_stages], tool_choice="required").ainvoke(
            [system_msg] + state["messages"], config=config
        )

        return {
            "messages": [response],
            "stats": _extract_usage(response),
        }

    async def model_node(state: AgentState, config: RunnableConfig):
        append_prompt = f"""
            Current stage: {state["stage_names"][state["current_stage"]]}
        """
        system_msg = SystemMessage(content=f"{system_prompt}\n\n{append_prompt}")

        response = await model.bind_tools(list(tools_dict.values()), tool_choice="auto").ainvoke(
            [system_msg] + state["messages"], config=config
        )

        return {
            "messages": [response],
            "stats": _extract_usage(response),
        }

    async def proceed_node(state: AgentState, config: RunnableConfig):
        """
        Called when model responded without tool calls.
        Forces the agent to either advance stages or edit them.
        Only end_current_stage and edit_stages are available here.
        """
        proceed_tools = [end_current_stage, edit_stages]

        curr_stage = state["current_stage"]
        total_stages = state["total_stages"]
        remaining_stages = [state["stage_names"][i] for i in range(curr_stage, total_stages)]

        append_prompt = f"""
            Stages are not finished yet.
            Remaining stages: {", ".join(remaining_stages)}
            You must now either:
            1. Call `end_current_stage` to advance to the next stage (or finish the task).
            2. Call `edit_stages` to replace all remaining stages with a new plan.
            You MUST call one of these tools.
        """
        system_msg = SystemMessage(content=f"{system_prompt}\n\n{append_prompt}")

        response = await model.bind_tools(proceed_tools, tool_choice="required").ainvoke(
            [system_msg] + state["messages"], config=config
        )

        return {
            "messages": [response],
            "stats": _extract_usage(response),
        }

    async def tools_node(state: AgentState, config: RunnableConfig):
        ai_msg = state["messages"][-1]
        new_messages: list[BaseMessage] = []
        stats_inc = {"tool_call_counts": 0, "failures": 0, "failures_since_last_reflection": 0}
        curr_idx = state["current_stage"]
        stage_names = list(state["stage_names"])
        total = state["total_stages"]
        is_done = False

        for call in ai_msg.tool_calls:
            name, args, call_id = call["name"], call["args"], call["id"]
            if name in tools_dict:
                tool = tools_dict[name]
            elif name == "build_stages":
                tool = build_stages
            else:
                tool = dummy_for_missed_tool
                tool.name = name
                args = {"name": name}

            try:
                output = await tool.ainvoke(args, config=config)

                if name == "build_stages":
                    stage_names, total = _handle_build_stages(output, config)
                    curr_idx = 0
                elif name == "end_current_stage":
                    curr_idx, is_done = _handle_end_stage(args, curr_idx, total, stage_names, config)
                elif name == "edit_stages":
                    stage_names, total = _handle_edit_stages(output, curr_idx, stage_names, config)

            except Exception as e:
                output = build_tool_response(success=False, message=f"Tool error: {e}")

            if not parse_tool_response(output).get("success"):
                stats_inc["failures"] += 1
                stats_inc["failures_since_last_reflection"] += 1

            stats_inc["tool_call_counts"] += 1
            new_messages.append(ToolMessage(content=output, tool_call_id=call_id, name=name))

        return {
            "messages": new_messages,
            "current_stage": curr_idx,
            "stage_names": stage_names,
            "total_stages": total,
            "task_completed": is_done,
            "stats": stats_inc,
        }

    async def reflection_node(state: AgentState, config: RunnableConfig):
        fail_count = state["stats"]["failures_since_last_reflection"]
        append_prompt = f"""
            You have accumulated {fail_count} failures in the previous steps.
            Please reflect on the failures and adjust your plan.
            Find out what went wrong and how to fix it.
            Recover from the failures and continue with the task.
        """
        system_msg = SystemMessage(content=f"{system_prompt}\n\n{append_prompt}")

        response = await model.ainvoke([system_msg] + state["messages"], config=config)

        return {
            "messages": [response],
            "stats": {**_extract_usage(response), "failures_since_last_reflection": -fail_count},
        }

    # --- Routing Logic ---

    def route_build(state: AgentState):
        if isinstance(state["messages"][-1], AIMessage) and state["messages"][-1].tool_calls:
            return "tools"
        # Retry
        return "build"

    def route_model(state: AgentState):
        if isinstance(state["messages"][-1], AIMessage) and state["messages"][-1].tool_calls:
            return "tools"
        fails = state["stats"].get("failures_since_last_reflection", 0)
        if fails > 0 and fails % app_config.model_reflection_threshold == 0:
            return "reflection"
        # Route to proceed node if no tool calls
        return "proceed"

    def route_proceed(state: AgentState):
        if isinstance(state["messages"][-1], AIMessage) and state["messages"][-1].tool_calls:
            return "tools"
        # Retry
        return "proceed"

    def route_tools(state: AgentState):
        # If task is completed, return END
        if state.get("task_completed"):
            return END
        # If build output is empty, retry
        if state.get("total_stages") == 0:
            return "build"
        # If reflection threshold is reached, return reflection
        fails = state["stats"].get("failures_since_last_reflection", 0)
        if fails > 0 and fails % app_config.model_reflection_threshold == 0:
            return "reflection"
        return "model"

    # --- Build Graph ---

    builder = StateGraph(AgentState)
    builder.add_node("build", build_node)
    builder.add_node("model", model_node)
    builder.add_node("proceed", proceed_node)
    builder.add_node("tools", tools_node)
    builder.add_node("reflection", reflection_node)

    builder.add_edge(START, "build")
    builder.add_conditional_edges("build", route_build, {"model": "model", "build": "build", "tools": "tools"})
    builder.add_conditional_edges(
        "model", route_model, {"tools": "tools", "proceed": "proceed", "reflection": "reflection"}
    )
    builder.add_conditional_edges("proceed", route_proceed, {"tools": "tools", "proceed": "proceed"})
    builder.add_conditional_edges(
        "tools", route_tools, {"model": "model", "reflection": "reflection", "build": "build", END: END}
    )
    builder.add_edge("reflection", "model")

    return builder.compile(checkpointer=checkpointer)


# --- Helper Functions ---


def _handle_build_stages(output, config):
    """Handle build_stages tool result. Returns (stage_names, stage_count)."""
    parsed = parse_tool_response(output)
    stages = parsed.get("data", {}).get("stage_names", [])
    if not stages:
        return [], 0, 0

    total = len(stages)

    dispatch_custom_event("stages_built", {"stages": stages}, config=config)
    dispatch_custom_event(
        "stage_started",
        {
            "stage_index": 0,
            "total_stages": total,
            "stage_name": stages[0],
        },
        config=config,
    )
    return stages, total


def _handle_end_stage(args, curr_idx, total, stage_names, config):
    """Handle end_current_stage tool result. Returns (curr_idx, is_done)."""
    stage_count = args.get("stage_count", 1)

    if stage_count == 0:
        return curr_idx, False

    start_idx = curr_idx
    end_idx = total if stage_count == -1 else min(start_idx + stage_count, total)

    completed_indices = list(range(start_idx, end_idx))
    if completed_indices:
        dispatch_custom_event("stages_completed", {"stage_indices": completed_indices}, config=config)

    curr_idx = end_idx
    if curr_idx >= total:
        return curr_idx, True

    dispatch_custom_event(
        "stage_started",
        {"stage_index": curr_idx, "total_stages": total, "stage_name": stage_names[curr_idx]},
        config=config,
    )
    return curr_idx, False


def _handle_edit_stages(output, curr_idx, stage_names, config):
    """Handle edit_stages tool result. Returns (stage_names, total)."""
    parsed_edit = parse_tool_response(output)
    new_stages = parsed_edit.get("data", {}).get("new_stages", [])
    if not new_stages:
        return stage_names, len(stage_names)

    stage_names = stage_names[:curr_idx] + new_stages
    total = len(stage_names)

    dispatch_custom_event(
        "stages_edited",
        {"stages": stage_names, "current_index": curr_idx},
        config=config,
    )
    return stage_names, total


def _extract_usage(response: AIMessage, tool_calls: int = 0) -> AgentStats:
    meta = getattr(response, "usage_metadata", {}) or {}
    return {
        "input_tokens": meta.get("input_tokens", 0),
        "output_tokens": meta.get("output_tokens", 0),
        "tool_call_counts": tool_calls or len(response.tool_calls),
        "failures": 0,
        "failures_since_last_reflection": 0,
    }
