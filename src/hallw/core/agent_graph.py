from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from hallw.tools import build_tool_response, dummy_for_missed_tool, parse_tool_response
from hallw.utils import config as hallw_config
from hallw.utils import logger

from .agent_state import AgentState, AgentStats


def build_graph(
    model: ChatOpenAI, tools_dict: dict[str, BaseTool], checkpointer: BaseCheckpointSaver
):
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

        if response.content:
            logger.info(f"HALLW: {response.content.strip().replace('\n', ' ')}")
        elif not response.tool_calls:
            # Empty response from model
            logger.info("HALLW: (empty). Retrying...")
            empty_response = True
            return {
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

        # Default to False, only set to True when no tool calls (task finished)
        task_completed_update = False

        # 1. Check for tool calls
        if not tool_calls:
            task_completed_update = True
            return {
                "messages": messages,
                "task_completed": task_completed_update,
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
                error_msg = f"Tool '{tool_name}' not found."
                logger.error(error_msg)

                # Use dummy tool for not found tools to avoid breaking the flow
                tool_obj = dummy_for_missed_tool
                tool_obj.name = tool_name
                tool_args = {"name": tool_name}

            # 2.2 Execute tool
            try:
                tool_response = await tool_obj.ainvoke(tool_args, config=config)
            except Exception as e:
                tool_response = build_tool_response(
                    success=False, message=f"Tool {tool_name} execution failed: {str(e)}"
                )
            stats_delta["tool_call_counts"] += 1

            messages.append(
                ToolMessage(content=tool_response, tool_call_id=tool_id, name=tool_name)
            )

            # 2.3 Parse result and log
            tool_result = parse_tool_response(tool_response)
            success = tool_result.get("success", False)

            logger.info(
                _build_log_str(
                    # Current total + this increment, for display only
                    state["stats"].get("tool_call_counts", 0) + stats_delta["tool_call_counts"],
                    tool_name,
                    tool_args,
                    success,
                )
            )

            if not success:
                stats_delta["failures"] += 1
                stats_delta["failures_since_last_reflection"] += 1

        return {
            "messages": messages,
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

        # 2. Temporarily build message list for this model call (do not directly modify state)
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
            logger.info(f"HALLW REFLECTION: {response.content.strip().replace('\n', ' ')}")

        # 5. Return
        return {"messages": [response], "stats": stats_delta}

    def route_from_model(state: AgentState) -> str:
        if state.get("empty_response", False):
            return "model"
        return "tools"

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

    builder.add_node("model", call_model)
    builder.add_node("tools", call_tool)
    builder.add_node("reflection", reflection)

    builder.add_edge(START, "model")
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


def _build_log_str(tool_call_count: int, tool_name: str, tool_args: dict, success: bool) -> str:
    status = "✅" if success else "❌"
    str_args = str(tool_args)
    format_tool_args = str_args[: hallw_config.max_message_chars]
    ellipsis = "..." if len(str_args) > hallw_config.max_message_chars else ""
    return f"[{tool_call_count}] {tool_name}: {format_tool_args}{ellipsis} => {status}"
