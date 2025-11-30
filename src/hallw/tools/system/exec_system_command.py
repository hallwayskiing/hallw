import asyncio
import locale
import platform
import uuid

from langchain_core.tools import tool

from hallw.tools import build_tool_response
from hallw.utils import Events, emit, subscribe, unsubscribe

# Maximum time (seconds) to wait for user confirmation
CONFIRM_TIMEOUT = 60


def _decode_output(raw: bytes) -> str:
    """Decode subprocess output safely using system-preferred encoding."""
    if raw is None:
        return ""
    encoding = locale.getpreferredencoding(False) or "utf-8"
    return raw.decode(encoding, errors="replace").strip()


def _select_backend(command: str) -> tuple[list[str], str]:
    """Choose the shell backend based on the host OS."""
    system_name = platform.system().lower()
    if system_name.startswith("win"):
        return ["powershell", "-Command", command], "PowerShell"
    return ["sh", "-c", command], "sh"


async def _run_system(command: str) -> str:
    """Execute the command with the appropriate shell and capture output."""
    cmd_args, backend_name = _select_backend(command)
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except Exception as exc:
        return build_tool_response(False, f"Failed to start {backend_name}: {exc}")

    stdout, stderr = await process.communicate()
    stdout_text = _decode_output(stdout)
    stderr_text = _decode_output(stderr)

    if process.returncode == 0:
        message = stdout_text or "Command completed without output."
        return build_tool_response(True, message)

    error_msg = stderr_text or stdout_text or f"{backend_name} exited with code {process.returncode}."
    return build_tool_response(False, error_msg)


@tool
async def exec_system_command(command: str) -> str:
    """Execute a system command, auto-selecting PowerShell on Windows or sh on POSIX.

    Args:
        command (str): The command to execute.

    Returns:
        str: The output of the command.
    """
    loop = asyncio.get_running_loop()
    request_id = str(uuid.uuid4())
    confirmation: asyncio.Future[bool] = loop.create_future()

    def _resolve(decision: bool) -> None:
        if not confirmation.done():
            confirmation.set_result(decision)

    def _on_user_choice(data: dict) -> None:
        if data.get("request_id") != request_id:
            return
        approved = bool(data.get("approved", False))
        loop.call_soon_threadsafe(_resolve, approved)

    subscribe(Events.SCRIPT_CONFIRM_RESPONDED, _on_user_choice)

    # Notify UI to request user confirmation
    emit(
        Events.SCRIPT_CONFIRM_REQUESTED,
        {
            "request_id": request_id,
            "command": command,
            "timeout": CONFIRM_TIMEOUT,
        },
    )

    try:
        approved = await asyncio.wait_for(confirmation, timeout=CONFIRM_TIMEOUT)
    except asyncio.TimeoutError:
        return build_tool_response(False, "Timed out waiting for user confirmation.")
    finally:
        unsubscribe(Events.SCRIPT_CONFIRM_RESPONDED, _on_user_choice)

    if not approved:
        return build_tool_response(False, "System command execution rejected by user.")

    return await _run_system(command)
