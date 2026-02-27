import os

from langchain_core.tools import tool

from hallw.tools import build_tool_response


@tool
async def write_file(file_path: str, content: str, mode: str = "w") -> str:
    """Write content to a file. Creates parent directories if they don't exist.

    Args:
        file_path (str): The absolute path to the file to write.
        content (str): The content to write to the file.
        mode (str): The mode to open the file. "w" for write, "a" for append.

    Returns:
        The content of the file or an error message.
    """
    # Normalize path
    file_path = os.path.normpath(file_path)

    # Determine if file exists (for confirmation message)
    file_exists = os.path.exists(file_path)
    if mode == "a" and not file_exists:
        return build_tool_response(False, f"File does not exist for append mode: {file_path}")

    # Create parent directories if needed
    parent_dir = os.path.dirname(file_path)
    if parent_dir and not os.path.exists(parent_dir):
        try:
            os.makedirs(parent_dir, exist_ok=True)
        except PermissionError:
            return build_tool_response(False, f"Permission denied creating directory: {parent_dir}")
        except Exception as e:
            return build_tool_response(False, f"Failed to create directory: {e}")

    # Write content to file
    try:
        with open(file_path, mode, encoding="utf-8") as f:
            f.write(content)
    except PermissionError:
        return build_tool_response(False, f"Permission denied: {file_path}")
    except Exception as e:
        return build_tool_response(False, f"Failed to write file: {e}")

    lines_written = content.count("\n") + (1 if content and not content.endswith("\n") else 0)

    return build_tool_response(
        True,
        f"Successfully wrote to file: {file_path}",
        {
            "file_path": file_path,
            "mode": mode,
            "bytes_written": len(content.encode("utf-8")),
            "lines_written": lines_written,
        },
    )
