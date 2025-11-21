import asyncio
import json

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from hallw.agent_state import AgentState
from hallw.tools import FINISH_TASK_TOOL_NAME, parse_tool_response
from hallw.utils import config as hallw_config
from hallw.utils import logger

# Configuration for model call retries
MAX_MODEL_RETRIES = 2
RETRY_BACKOFF_SECONDS = 1.0


def _format_tool_args(tool_args: object, limit: int) -> str:
    """Format tool arguments for logging with truncation.

    Args:
        tool_args: Tool arguments to format (typically dict or other object)
        limit: Maximum character limit for formatted output

    Returns:
        Formatted string, truncated with '...' if exceeding limit
    """
    try:
        formatted = json.dumps(tool_args, ensure_ascii=False)
    except (TypeError, ValueError):
        formatted = str(tool_args)

    if len(formatted) > limit:
        return formatted[:limit] + "..."
    return formatted


def build_graph(model: ChatOpenAI, tools_dict: dict[str, BaseTool]):
    async def call_model(state: AgentState, config: RunnableConfig) -> AgentState:
        response = None

        for attempt in range(MAX_MODEL_RETRIES + 1):
            try:
                async for chunk in model.astream(state["messages"], config=config):
                    response = chunk if response is None else response + chunk

                if response is None:
                    raise RuntimeError("Model returned no response")

                # Success - break out of retry loop
                break

            except Exception as e:
                if attempt < MAX_MODEL_RETRIES:
                    logger.warning(
                        f"Model call failed (attempt {attempt + 1}/{MAX_MODEL_RETRIES + 1}): {e}. "
                        f"Retrying in {RETRY_BACKOFF_SECONDS}s..."
                    )
                    await asyncio.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
                    response = None  # Reset for retry
                else:
                    # All retries exhausted
                    raise RuntimeError(
                        f"Model call failed after {MAX_MODEL_RETRIES + 1} attempts"
                    ) from e

        if response.usage_metadata:
            state["stats"]["input_tokens"] += response.usage_metadata.get("input_tokens", 0)
            state["stats"]["output_tokens"] += response.usage_metadata.get("output_tokens", 0)

        if response.content:
            logger.info(f"HALLW: {response.content.strip().replace('\n', ' ')}")

        return {
            "messages": [response],
            "task_completed": state["task_completed"],
            "stats": state["stats"],
        }

    async def call_tool(state: AgentState, config: RunnableConfig) -> AgentState:
        ai_message = state["messages"][-1]
        tool_calls = ai_message.tool_calls
        stats = state["stats"]
        messages = []
        if not tool_calls:
            warning_msg = "No tool call found in the your response. Please specify tools to call."
            messages.append(HumanMessage(content=warning_msg))
            stats["failures"] += 1

        for tool_call in tool_calls:
            tool_id = tool_call.get("id")
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args") or {}
            tool_obj = tools_dict.get(tool_name)

            if tool_obj is None:
                error_msg = f"Tool '{tool_name}' not found."
                logger.error(error_msg)
                messages.append(
                    ToolMessage(content=error_msg, tool_call_id=tool_id, name=tool_name)
                )
                stats["failures"] += 1
                continue

            tool_response = await tool_obj.ainvoke(tool_args, config=config)

            stats["tool_call_counts"] += 1

            messages.append(
                ToolMessage(content=tool_response, tool_call_id=tool_id, name=tool_name)
            )

            parsed_response = parse_tool_response(tool_response)
            success = parsed_response["success"]

            # Log tool call result to file
            formatted_args = _format_tool_args(tool_args, hallw_config.max_message_chars)
            logger.info(
                f"[{stats['tool_call_counts']}] {tool_name}({formatted_args}) "
                f"=> {'✅' if success else '❌'}"
            )

            if not success:
                stats["failures"] += 1

            if tool_name == FINISH_TASK_TOOL_NAME:
                state["task_completed"] = True

        return {
            "messages": messages,
            "task_completed": state["task_completed"],
            "stats": state["stats"],
        }

    async def reflection(state: AgentState, config: RunnableConfig) -> AgentState:
        # let llm reflect for failures
        stats = state["stats"]

        hint_message = f"""
        System Notification:
        You have accumulated a total of {stats['failures']} failures during this task so far.
        The most recent action also failed.

        Please stop and reflect:
        1. Analyze why the previous steps failed.
        2. Adjust your plan to avoid repeating the same mistakes.
        3. Propose the next correct tool call.
        """

        state["messages"].append(HumanMessage(content=hint_message.strip()))

        return await call_model(state, config)

    def route_from_tools(state: AgentState) -> str:
        if state["task_completed"]:
            return "end"

        stats = state["stats"]
        # Trigger reflection after every 3 failures, but only once per group of 3
        # failures=3,6,9... should trigger reflection if not already done for that batch
        if stats["failures"] > 0 and stats["failures"] % 3 == 0:
            # Check if we haven't already reflected for this batch
            expected_reflections = stats["failures"] // 3
            if stats["reflections"] < expected_reflections:
                stats["reflections"] += 1
                return "reflection"

        return "model"

    builder = StateGraph(AgentState)

    builder.add_node("model", call_model)
    builder.add_node("tools", call_tool)
    builder.add_node("reflection", reflection)

    builder.add_edge(START, "model")
    builder.add_edge("model", "tools")
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

    checkpointer = MemorySaver()

    workflow = builder.compile(checkpointer=checkpointer)

    return workflow, checkpointer
