import os
from itertools import islice

from langchain_core.tools import tool

from hallw.tools import build_tool_response

READ_LINES_LIMIT = 1000


@tool
def read(file_path: str, start_line: int = 0, end_line: int = -1) -> str:
    """Read the content of a file.

    Args:
        file_path: The absolute path to the file to read.
        start_line: The starting line number (inclusive).
        end_line: The ending line number (exclusive). Use -1 to read until the end.

    Returns:
        str: The content of the file or an error message.
    """
    # Normalize path
    file_path = os.path.normpath(file_path)

    if not os.path.exists(file_path):
        return build_tool_response(False, f"File not found: {file_path}")

    if not os.path.isfile(file_path):
        return build_tool_response(False, f"Path is not a file: {file_path}")

    # Validate start_line
    if start_line < 0:
        start_line = 0

    if end_line != -1 and start_line > end_line:
        return build_tool_response(
            False,
            f"Start line ({start_line}) cannot be greater than end line ({end_line}).",
        )

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            it = islice(f, start_line, None if end_line == -1 else end_line)
            lines = []
            for i, line in enumerate(it, start=start_line):
                if i - start_line >= READ_LINES_LIMIT:
                    break
                lines.append(line)

        if not lines:
            return build_tool_response(
                False,
                f"No content found in the specified line range ({start_line}-{end_line}).",
            )

        content = "".join(lines)

        return build_tool_response(
            True,
            "Read file successfully.",
            {
                "file_path": file_path,
                "start_line": start_line,
                "end_line": start_line + len(lines),
                "lines_read": len(lines),
                "content": content,
            },
        )

    except PermissionError:
        return build_tool_response(False, f"Permission denied: {file_path}")
    except UnicodeDecodeError:
        return build_tool_response(
            False,
            "File appears to be binary. Consider using a different tool.",
        )
    except Exception as e:
        return build_tool_response(False, f"Failed to read file: {e}")
