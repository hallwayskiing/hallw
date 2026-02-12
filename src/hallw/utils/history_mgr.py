import json
import logging
from typing import Any, Dict, List, Optional

import aiosqlite
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from hallw.tools import parse_tool_response

logger = logging.getLogger("hallw")

# --- Global Persistence State ---
conn: Optional[aiosqlite.Connection] = None
checkpointer: Optional[AsyncSqliteSaver] = None


async def get_checkpointer() -> AsyncSqliteSaver:
    global conn, checkpointer
    if checkpointer is None:
        conn = await aiosqlite.connect("checkpoints.db", check_same_thread=False)
        checkpointer = AsyncSqliteSaver(conn)
        await checkpointer.setup()
    return checkpointer


async def get_all_threads() -> List[Dict[str, Any]]:
    """Fetches a summary list of all conversation threads."""
    cp = await get_checkpointer()
    async with conn.execute("SELECT DISTINCT thread_id FROM checkpoints") as cursor:
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
                        content = str(msg.content)
                        if content.startswith("User: "):
                            content = content[6:]
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


async def load_thread(thread_id: str) -> Optional[Dict[str, Any]]:
    """Loads state for a specific thread."""
    cp = await get_checkpointer()
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


async def delete_thread(thread_id: str) -> None:
    """Deletes a thread and all associated checkpoints."""
    await get_checkpointer()  # Ensure conn is active
    await conn.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
    await conn.execute("DELETE FROM checkpoint_blobs WHERE thread_id = ?", (thread_id,))
    await conn.execute("DELETE FROM checkpoint_writes WHERE thread_id = ?", (thread_id,))
    await conn.commit()


def serialize_messages(messages: List[Any]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Serializes LangChain messages for the frontend and reconstructs tool states.
    Returns (serialized_msgs, restored_tool_states)
    """
    serialized_msgs = []
    restored_tool_states = []
    local_tool_map: Dict[str, Any] = {}

    for msg in messages:
        role = ""
        content = ""
        reasoning = ""

        if isinstance(msg, HumanMessage):
            role = "user"
            content = str(msg.content)
            if content.startswith("User: "):
                content = content[6:]
            serialized_msgs.append(
                {
                    "role": role,
                    "type": "text",
                    "content": content,
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
                        "role": role,
                        "type": "text",
                        "content": content,
                        "reasoning": reasoning,
                    }
                )

            if hasattr(msg, "tool_calls"):
                for call in msg.tool_calls:
                    local_tool_map[call["id"]] = call["args"]

        elif isinstance(msg, ToolMessage):
            parsed = parse_tool_response(str(msg.content))

            restored_tool_states.append(
                {
                    "run_id": msg.tool_call_id,
                    "tool_name": msg.name,
                    "status": "success" if parsed["success"] else "error",
                    "args": json.dumps(local_tool_map.get(msg.tool_call_id, {}), ensure_ascii=False)
                    if isinstance(local_tool_map.get(msg.tool_call_id), (dict, list))
                    else str(local_tool_map.get(msg.tool_call_id, "")),
                    "result": str(msg.content),
                }
            )

    return serialized_msgs, restored_tool_states
