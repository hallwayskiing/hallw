import os

from langchain_core.tools import tool

from hallw.tools import build_tool_response


@tool
async def edit_file(file_path: str, old_str: str, new_str: str) -> str:
    """Edit a specific block of text in a file with new content.

    Args:
        file_path (str): The absolute path to the file to edit.
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
            f"Successfully edited the file: {file_path}",
            {
                "file_path": file_path,
                "bytes_written": len(new_str.encode("utf-8")),
                "lines_written": new_str.count("\n") + (1 if new_str and not new_str.endswith("\n") else 0),
            },
        )

    except PermissionError:
        return build_tool_response(False, f"Permission denied: {file_path}")
    except Exception as e:
        return build_tool_response(False, f"Failed to edit file: {str(e)}")
