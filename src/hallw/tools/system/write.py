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


@tool
async def replace_file_block(file_path: str, old_str: str, new_str: str) -> str:
    """Replace a specific block of text in a file with new content.
    This is the preferred tool for modifying large files to save tokens and time.

    Args:
        file_path (str): The absolute path to the file to modify.
        old_str (str): The EXACT text sequence in the file to be replaced.
        new_str (str): The new text to replace the old_str with.

    Returns:
        A status message indicating success or details of any failure.
    """
    file_path = os.path.normpath(file_path)

    if not os.path.exists(file_path):
        return build_tool_response(False, f"File not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Count occurrences to ensure we're not replacing the wrong thing
        count = content.count(old_str)
        if count == 0:
            return build_tool_response(
                False,
                "The search block was not found. Ensure whitespace and characters match exactly.",
            )
        if count > 1:
            return build_tool_response(
                False,
                f"The search block appeared {count} times. Provide a more unique block.",
            )

        new_content = content.replace(old_str, new_str)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return build_tool_response(
            True,
            f"Successfully replaced the block in {file_path}",
            {
                "file_path": file_path,
                "bytes_written": len(new_str.encode("utf-8")),
                "lines_written": new_str.count("\n") + (1 if new_str and not new_str.endswith("\n") else 0),
            },
        )

    except PermissionError:
        return build_tool_response(False, f"Permission denied: {file_path}")
    except Exception as e:
        return build_tool_response(False, f"Failed to replace block: {str(e)}")
