import asyncio
import locale
import platform
import uuid

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from hallw.tools import build_tool_response
from hallw.utils import config as app_config

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


def _is_command_blacklisted(command: str, blacklist: list[str]) -> bool:
    """Check if command contains any blacklisted keywords."""
    command_lower = command.lower()
    for keyword in blacklist:
        if keyword.lower() in command_lower:
            return True
    return False


@tool
async def exec(command: str, config: RunnableConfig) -> str:
    """Execute a system command. Use `sh` on Linux or `powershell` on Windows.

    Args:
        command (str): The command to execute.

    Returns:
        str: The output of the command.
    """
    # Get renderer from config's configurable
    renderer = config.get("configurable", {}).get("renderer")
    if renderer is None:
        return build_tool_response(False, "Internal error: renderer not available.")

    # Check auto-allow settings
    auto_allow = getattr(app_config, "auto_allow_exec", False)
    blacklist = getattr(app_config, "auto_allow_blacklist", [])

    if not auto_allow or _is_command_blacklisted(command, blacklist):
        request_id = str(uuid.uuid4())
        status = await renderer.on_request_confirmation(
            request_id,
            CONFIRM_TIMEOUT,
            f"System command execution: {command}",
        )

        if status == "timeout":
            return build_tool_response(False, "Timed out waiting for user confirmation.")
        if status == "rejected":
            return build_tool_response(False, "System command execution rejected by user.")

    return await _run_system(command)
