import asyncio
import locale
import os
import platform
import shlex
import uuid
from typing import List, Optional

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from hallw.tools import build_tool_response
from hallw.utils import config as app_config

CONFIRM_TIMEOUT = 60
EXEC_COMMAND_TIMEOUT = 30
MAX_OUTPUT_ROWS = 500


@tool
async def exec(command: str, config: RunnableConfig) -> str:
    """Execute a system command. Use **PowerShell** in Windows and **sh** in Linux.

    Args:
        command: The direct command to execute.

    Returns:
        str: The result of the command execution or error message.
    """
    auto_allow = app_config.auto_allow_exec
    blacklist = app_config.auto_allow_blacklist

    if not auto_allow or _is_command_blacklisted(command, blacklist):
        renderer = config.get("configurable", {}).get("renderer")
        if renderer is None:
            return build_tool_response(False, "Renderer not found.")

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


async def _run_system(command: str) -> str:
    cmd_args, backend_name = _select_backend(command)

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except Exception as exc:
        return build_tool_response(False, f"Failed to start {backend_name}: {exc}")

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=EXEC_COMMAND_TIMEOUT)
    except asyncio.TimeoutError:
        await _cleanup_process(process, 3)
        return build_tool_response(False, f"Command execution timed out after {EXEC_COMMAND_TIMEOUT} seconds.")
    except Exception as exc:
        await _cleanup_process(process, 1)
        return build_tool_response(False, f"Execution failed: {exc}")

    stdout_text = _decode_output(stdout)
    stderr_text = _decode_output(stderr)

    return build_tool_response(
        process.returncode == 0,
        "Command executed.",
        {
            "stdout": stdout_text,
            "stderr": stderr_text,
            "returncode": process.returncode,
        },
    )


def _select_backend(command: str) -> tuple[list[str], str]:
    system_name = platform.system().lower()
    if system_name.startswith("win"):
        return [
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            (
                "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; "
                "if (Test-Path Alias:R) { Remove-Item Alias:R -Force }; "
                f"$__out = $({command}); "
                "if ($__out -ne $null) { $__out | Out-String -Width 4096 }; "
                "if ($LASTEXITCODE) { exit $LASTEXITCODE }"
            ),
        ], "PowerShell"
    return ["sh", "-c", command], "sh"


async def _cleanup_process(process, timeout=1):
    if process.returncode is not None:
        return
    try:
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
    except Exception:
        pass


def _decode_output(raw: bytes) -> str:
    if not raw:
        return ""

    text = None
    for enc in ["utf-8", locale.getpreferredencoding(False), "gbk"]:
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue

    if text is None:
        text = raw.decode("utf-8", errors="replace")

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines = [line.rstrip() for line in text.split("\n")]

    compact = []
    prev_blank = False
    for line in lines:
        blank = not line.strip()
        if blank and prev_blank:
            continue
        compact.append(line)
        prev_blank = blank

    # ---- LIMIT OUTPUT ----
    if len(compact) > MAX_OUTPUT_ROWS:
        truncated = len(compact) - MAX_OUTPUT_ROWS
        head = MAX_OUTPUT_ROWS // 2
        tail = MAX_OUTPUT_ROWS - head
        compact = compact[:head] + [f"... ({truncated} lines truncated) ..."] + compact[-tail:]

    return "\n".join(compact).strip()


def _extract_commands(command: str) -> List[str]:
    separators = {"&&", "||", "|", ";"}

    posix = not platform.system().lower().startswith("win")

    lexer = shlex.shlex(command, posix=posix)
    lexer.whitespace_split = True
    lexer.commenters = ""

    tokens = list(lexer)

    cmds: list[str] = []
    current: list[str] = []

    for tok in tokens:
        if tok in separators:
            if current:
                cmds.append(" ".join(current))
                current = []
        else:
            current.append(tok)

    if current:
        cmds.append(" ".join(current))

    return cmds


def _get_command_name(command: str) -> Optional[str]:
    if any(x in command for x in ("&&", ";", "|", "\n", "\r")):
        return None

    try:
        if platform.system().lower().startswith("win"):
            parts = shlex.split(command, posix=False)
        else:
            parts = shlex.split(command, posix=True)
    except ValueError:
        return None

    if not parts:
        return None

    cmd = parts[0]
    cmd = os.path.basename(cmd)
    cmd = os.path.splitext(cmd)[0]
    cmd = cmd.split(".")[0]

    return cmd.lower()


def _is_command_blacklisted(command: str, blacklist: List[str]) -> bool:
    _blacklist = {b.lower() for b in blacklist}

    for cmd in _extract_commands(command):
        name = _get_command_name(cmd)
        if name in _blacklist:
            return True

    return False
