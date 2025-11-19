from pathlib import Path

from langchain_core.tools import tool

from hallw.tools import build_tool_response
from hallw.utils import config, logger


@tool
def file_save(file_path: str, content: str, format: str = "md") -> str:
    """Save content to a file. Default format is 'md'.

    Args:
        file_path: Path where to save the file
        content: Text content to save
        format: Output format - You can decide to save in formats you prefer, supporting all the text formats like 'txt' and 'md', and source codes.

    Returns:
        Success/error message with file path
    """
    try:
        # Ensure file_path has extension (use absolute path for file ops)
        base_dir = Path(config.file_base_dir).resolve()
        target_path = (base_dir / file_path).resolve()

        # Add extension if missing
        if not target_path.suffix:
            target_path = target_path.with_suffix(".md")

        # Create parent directories if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(str(target_path), "w", encoding="utf-8") as f:
            f.write(content)

        file_size = len(content)
        logger.info(f"file_save: Saved {file_size} chars to {target_path}")
        return build_tool_response(
            True, "File saved successfully.", {"path": str(target_path), "size": file_size}
        )

    except Exception as e:
        logger.error(f"file_save error: {e}")
        return build_tool_response(False, f"Failed to save file: {e}")


@tool
def file_append(file_path: str, content: str) -> str:
    """Append content to an existing text file.

    Args:
        file_path: Path to the file
        content: Text content to append

    Returns:
        Success/error message
    """
    try:
        # Ensure file_path has extension (use absolute path for file ops)
        base_dir = Path(config.file_base_dir).resolve()
        target_path = (base_dir / file_path).resolve()

        # Add extension if missing
        if not target_path.suffix:
            target_path = target_path.with_suffix(".md")

        # Create parent directories if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(str(target_path), "a", encoding="utf-8") as f:
            f.write(content)

        file_size = len(content)
        logger.info(f"file_save: Saved {file_size} chars to {target_path}")
        return build_tool_response(
            True, "File saved successfully.", {"path": str(target_path), "size": file_size}
        )

    except Exception as e:
        logger.error(f"file_save error: {e}")
        return build_tool_response(False, f"Failed to save file: {e}")
