from typing import Dict, cast

from langchain_core.callbacks.manager import dispatch_custom_event
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from hallw.tools import build_stages, build_tool_response, dummy_for_missed_tool, parse_tool_response
from hallw.utils import config as hallw_config

from .agent_state import AgentState


def build_graph(model, tools_dict, checkpointer) -> StateGraph:
    """
    Builds the LangGraph workflow
    """

    # --- Nodes ---

    async def build_node(state: AgentState, config: RunnableConfig):
        planner = model.bind_tools([build_stages], tool_choice="required")
        response = await planner.ainvoke(state["messages"], config=config)

        tool_call = response.tool_calls[0]
        result = await build_stages.ainvoke(tool_call["args"], config=config)
        parsed = parse_tool_response(result)
        stages = parsed.get("data", {}).get("stage_names", [])

        dispatch_custom_event("stages_built", {"stages": stages}, config=config)

        node_output = {
            "messages": [
                response,
                ToolMessage(content=result, tool_call_id=tool_call["id"], name="build_stages"),
                SystemMessage(content=f"Stage 1/{len(stages)} started: {stages[0]}"),
            ],
            "stage_names": stages,
            "total_stages": len(stages),
            "current_stage": 0,
            "stats": _extract_usage(response, tool_calls=1),
        }
        _dispatch_stage_event("stage_started", 0, cast(AgentState, node_output), config)
        return node_output

    async def model_node(state: AgentState, config: RunnableConfig):
        messages = state["messages"]
        if isinstance(messages[-1], AIMessage) and not messages[-1].tool_calls:
            messages = messages + [SystemMessage(content="Stages not completed. Please continue your task.")]

        response = await model.ainvoke(messages, config=config)

        reasoning = (
            getattr(response, "reasoning_content", None) or response.additional_kwargs.get("reasoning_content") or ""
        )
        is_empty = not (response.content.strip() or response.tool_calls or reasoning)
        stats = _extract_usage(response)

        if is_empty:
            stats["failures"] = 1
            stats["failures_since_last_reflection"] = 1
            # Add a prompt to the model to retry
            messages = [
                response,
                SystemMessage(content="Your last response was empty. Please provide a valid response."),
            ]
        else:
            messages = [response]

        return {
            "messages": messages,
            "stats": stats,
        }

    async def tools_node(state: AgentState, config: RunnableConfig):
        ai_msg = state["messages"][-1]
        new_messages = []
        stats_inc = {"tool_call_counts": 0, "failures": 0, "failures_since_last_reflection": 0}
        curr_idx = state["current_stage"]
        is_done = False

        for call in ai_msg.tool_calls:
            name, args, call_id = call["name"], call["args"], call["id"]
            if name not in tools_dict:
                tool = dummy_for_missed_tool
                tool.name = name
                args = {"name": name}
            else:
                tool = tools_dict[name]

            try:
                output = await tool.ainvoke(args, config=config)
                if name == "end_current_stage":
                    _dispatch_stage_event("stage_completed", curr_idx, state, config)
                    curr_idx += 1
                    if curr_idx >= state["total_stages"]:
                        is_done = True
                    else:
                        _dispatch_stage_event("stage_started", curr_idx, state, config)
                        stage_info = f"Stage {curr_idx+1}/{state['total_stages']}: {state['stage_names'][curr_idx]}"
                        new_messages.append(SystemMessage(content=stage_info))
            except Exception as e:
                output = build_tool_response(success=False, message=f"Tool error: {e}")

            if not parse_tool_response(output).get("success"):
                stats_inc["failures"] += 1
                stats_inc["failures_since_last_reflection"] += 1

            stats_inc["tool_call_counts"] += 1
            new_messages.append(ToolMessage(content=output, tool_call_id=call_id, name=name))

        return {"messages": new_messages, "current_stage": curr_idx, "task_completed": is_done, "stats": stats_inc}

    async def reflection_node(state: AgentState, config: RunnableConfig):
        fail_count = state["stats"]["failures_since_last_reflection"]
        reflection_prompt = f"""
        You have accumulated {fail_count} failures in the previous steps.
        Please reflect on the failures and adjust your plan.
        Use your reasoning.
        """
        hint = HumanMessage(content=reflection_prompt)
        response = await model.ainvoke(state["messages"] + [hint], config=config)
        return {
            "messages": [hint, response],
            "stats": {**_extract_usage(response), "failures_since_last_reflection": -fail_count},
        }

    # --- Routing Logic ---

    def route_model(state: AgentState):
        if isinstance(state["messages"][-1], AIMessage) and state["messages"][-1].tool_calls:
            return "tools"

        fails = state["stats"].get("failures_since_last_reflection", 0)
        if fails > 0 and fails % hallw_config.model_reflection_threshold == 0:
            return "reflection"

        return "model"

    def route_tools(state: AgentState):
        if state.get("task_completed"):
            return END
        fails = state["stats"].get("failures_since_last_reflection", 0)
        if fails > 0 and fails % hallw_config.model_reflection_threshold == 0:
            return "reflection"
        return "model"

    def route_reflection(state: AgentState):
        if isinstance(state["messages"][-1], AIMessage) and state["messages"][-1].tool_calls:
            return "tools"
        return "model"

    # --- Internal Helpers ---

    def _extract_usage(response: AIMessage, tool_calls: int = 0) -> Dict:
        meta = getattr(response, "usage_metadata", {}) or {}
        return {
            "input_tokens": meta.get("input_tokens", 0),
            "output_tokens": meta.get("output_tokens", 0),
            "tool_call_counts": tool_calls or len(response.tool_calls),
            "failures": 0,
            "failures_since_last_reflection": 0,
        }

    def _dispatch_stage_event(kind: str, idx: int, state: AgentState, config: RunnableConfig):
        dispatch_custom_event(
            kind,
            {
                "stage_index": idx,
                "total_stages": state.get("total_stages", 0),
                "stage_name": state["stage_names"][idx] if idx < len(state["stage_names"]) else "Done",
            },
            config=config,
        )

    # --- Build Graph ---

    builder = StateGraph(AgentState)
    builder.add_node("build", build_node)
    builder.add_node("model", model_node)
    builder.add_node("tools", tools_node)
    builder.add_node("reflection", reflection_node)

    builder.add_edge(START, "build")
    builder.add_edge("build", "model")
    builder.add_conditional_edges(
        "model", route_model, {"tools": "tools", "model": "model", "reflection": "reflection"}
    )
    builder.add_conditional_edges("tools", route_tools, {"model": "model", "reflection": "reflection", END: END})
    builder.add_conditional_edges("reflection", route_reflection, {"model": "model", "tools": "tools"})

    return builder.compile(checkpointer=checkpointer)
