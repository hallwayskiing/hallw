import json
import logging
import os
from typing import Any

import aiosqlite
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from hallw.tools import parse_tool_response

logger = logging.getLogger("hallw")


async def create_local_checkpointer() -> tuple[aiosqlite.Connection, AsyncSqliteSaver]:
    """Creates a new db connection and checkpointer bound to the current asyncio loop."""
    local_conn = await aiosqlite.connect("checkpoints.db", check_same_thread=False)
    local_cp = AsyncSqliteSaver(local_conn)
    await local_cp.setup()
    return local_conn, local_cp


async def get_all_threads() -> list[dict[str, Any]]:
    """Fetches a summary list of all conversation threads."""
    local_conn, cp = await create_local_checkpointer()

    try:
        async with local_conn.execute("SELECT DISTINCT thread_id FROM checkpoints") as cursor:
            rows = await cursor.fetchall()
            thread_ids = [row[0] for row in rows]

        threads = []
        for tid in thread_ids:
            # Get latest checkpoint for this thread to find some metadata
            latest = await cp.aget_tuple({"configurable": {"thread_id": tid}})
            if latest:
                # Extract Title from first HumanMessage
                title = "New Conversation"
                created_at = None

                # Check messages in channel values
                if latest.checkpoint and "channel_values" in latest.checkpoint:
                    messages = latest.checkpoint["channel_values"].get("messages", [])
                    for msg in messages:
                        if isinstance(msg, HumanMessage):
                            content = ""
                            if isinstance(msg.content, list):
                                content = msg.content[-1].get("text", "")
                                if not content:
                                    content = "Attached Files"
                            else:
                                content = str(msg.content)
                            title = content.strip()
                            break

                # Extract Timestamp
                if latest.metadata:
                    created_at = latest.metadata.get("created_at") or latest.metadata.get("ts")

                # Fallback to checkpoint timestamp
                if not created_at and latest.checkpoint:
                    created_at = latest.checkpoint.get("ts")

                threads.append({"id": tid, "title": title, "created_at": created_at, "metadata": latest.metadata})

        # Sort by created_at desc
        threads.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
        return threads
    finally:
        await local_conn.close()


async def load_thread(thread_id: str) -> dict[str, Any] | None:
    """Loads state for a specific thread."""
    local_conn, cp = await create_local_checkpointer()
    try:
        checkpoint_tuple = await cp.aget_tuple({"configurable": {"thread_id": thread_id}})
        if not checkpoint_tuple:
            return None

        state = checkpoint_tuple.checkpoint["channel_values"]
        messages = state.get("messages", [])
        stats = state.get("stats", {})

        serialized_msgs, tool_states = serialize_messages(messages)

        return {
            "messages": messages,  # Raw messages for backend session
            "stats": stats,
            "serialized_msgs": serialized_msgs,  # For frontend
            "tool_states": tool_states,  # For frontend
        }
    finally:
        await local_conn.close()


async def delete_thread(thread_id: str) -> None:
    """Deletes a thread and all associated checkpoints."""
    local_conn, _ = await create_local_checkpointer()
    try:
        await local_conn.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
        await local_conn.execute("DELETE FROM writes WHERE thread_id = ?", (thread_id,))
        await local_conn.commit()
    finally:
        await local_conn.close()


async def delete_all_threads() -> None:
    """Deletes all threads and all associated checkpoints."""
    local_conn, _ = await create_local_checkpointer()
    try:
        await local_conn.execute("DELETE FROM checkpoints")
        await local_conn.execute("DELETE FROM writes")
        await local_conn.commit()
    finally:
        await local_conn.close()


def serialize_messages(messages: list[Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Serializes LangChain messages for the frontend and reconstructs tool states.
    Returns (serialized_msgs, restored_tool_states)
    """
    serialized_msgs = []
    restored_tool_states = []
    local_tool_map: dict[str, dict[str, Any]] = {}

    for msg in messages:
        role = ""
        content = ""
        reasoning = ""
        message_id = str(getattr(msg, "id", "") or "")

        if isinstance(msg, HumanMessage):
            role = "user"
            content = msg.content
            res = ""
            if isinstance(content, list):
                res = content[-1].get("text", "")
                file_paths = msg.additional_kwargs.get("files", [])
                for file_path in file_paths:
                    res += f"\n 🔗 *{os.path.basename(file_path)}*"
            else:
                res = str(msg.content)
            serialized_msgs.append(
                {
                    "id": message_id,
                    "role": role,
                    "type": "text",
                    "content": res,
                }
            )

        elif isinstance(msg, SystemMessage):
            continue

        elif isinstance(msg, AIMessage):
            role = "assistant"
            content = str(msg.content)
            try:
                reasoning = (
                    msg.response_metadata.get("reasoning_content", "") if hasattr(msg, "response_metadata") else ""
                )
                if not reasoning and hasattr(msg, "additional_kwargs"):
                    reasoning = msg.additional_kwargs.get("reasoning_content", "")
            except Exception:
                reasoning = ""

            if content.strip() or reasoning.strip():
                serialized_msgs.append(
                    {
                        "id": message_id,
                        "role": role,
                        "type": "text",
                        "content": content,
                        "reasoning": reasoning,
                    }
                )

            if hasattr(msg, "tool_calls"):
                for call in msg.tool_calls:
                    local_tool_map[call["id"]] = {
                        "name": call.get("name", ""),
                        "args": call.get("args", {}),
                    }

        elif isinstance(msg, ToolMessage):
            parsed = parse_tool_response(str(msg.content))
            tool_call_meta = local_tool_map.get(msg.tool_call_id, {})
            tool_name = msg.name or tool_call_meta.get("name", "")
            tool_args = tool_call_meta.get("args", {})

            if tool_name == "request_user_decision":
                prompt = ""
                choices: list[str] | None = None
                if isinstance(tool_args, dict):
                    prompt = str(tool_args.get("prompt", ""))
                    raw_choices = tool_args.get("choices")
                    if isinstance(raw_choices, list):
                        choices = [str(choice) for choice in raw_choices]
                    elif raw_choices is not None:
                        choices = [str(raw_choices)]

                result = ""
                status = "submitted"
                if parsed["success"]:
                    result = str(parsed.get("data", {}).get("user_input", ""))
                else:
                    message = parsed.get("message", "")
                    status = "timeout" if "timed out" in message.lower() else "rejected"

                decision_message: dict[str, Any] = {
                    "id": message_id,
                    "role": "system",
                    "type": "decision",
                    "requestId": msg.tool_call_id or msg.id,
                    "prompt": prompt,
                    "choices": choices,
                    "result": result,
                    "status": status,
                }
                serialized_msgs.append(decision_message)

            restored_tool_states.append(
                {
                    "run_id": msg.id,
                    "tool_name": tool_name,
                    "status": "success" if parsed["success"] else "error",
                    "args": json.dumps(tool_args, ensure_ascii=False)
                    if isinstance(tool_args, (dict, list))
                    else str(tool_args),
                    "result": str(msg.content),
                }
            )

    merged_msgs: list[dict[str, Any]] = []
    for msg in serialized_msgs:
        is_ai_text = msg.get("role") == "assistant" and msg.get("type") == "text"

        if not merged_msgs:
            merged_msgs.append(msg)
            continue

        last_msg = merged_msgs[-1]
        is_last_ai_text = last_msg.get("role") == "assistant" and last_msg.get("type") == "text"

        if is_ai_text and is_last_ai_text:
            # Merge reasoning
            r1 = last_msg.get("reasoning", "")
            r2 = msg.get("reasoning", "")
            if r1 and r2:
                last_msg["reasoning"] = r1.rstrip() + "\n\n" + r2.lstrip()
            elif r2:
                last_msg["reasoning"] = r2

            # Merge content
            c1 = last_msg.get("content", "")
            c2 = msg.get("content", "")
            if c1 and c2:
                last_msg["content"] = c1.rstrip() + "\n\n" + c2.lstrip()
            elif c2:
                last_msg["content"] = c2
        else:
            merged_msgs.append(msg)

    return merged_msgs, restored_tool_states
