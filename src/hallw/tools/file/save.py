from pathlib import Path

from langchain_core.tools import tool

from hallw.tools import build_tool_response
from hallw.utils import config, logger


@tool
def file_save(file_path: str, content: str, format: str = "md") -> str:
    """Save content to a file. Overwrites if file exists.

    Args:
        file_path: Relative path where to save the file (e.g., "docs/summary.md").
                   If no extension is provided, the 'format' argument is used.
        content: Text content to save.
        format: Default extension to use if file_path doesn't have one (e.g., "json", "txt").

    Returns:
        Success message with the saved path and size.
    """
    try:
        # Resolve path using the format argument as a fallback extension
        target_path = _resolve_target_path(file_path, default_ext=format)

        # Write content (Overwrites existing file)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

        file_size = len(content)
        logger.info(f"file_save: Saved {file_size} chars to {target_path}")

        return build_tool_response(
            True, "File saved successfully.", {"path": str(target_path), "size": file_size}
        )

    except ValueError as ve:
        # Security/Path errors
        return build_tool_response(False, str(ve))
    except Exception as e:
        logger.error(f"file_save error: {e}")
        return build_tool_response(False, f"Failed to save file: {e}")


@tool
def file_append(file_path: str, content: str) -> str:
    """Append content to an existing file. Creates the file if it doesn't exist.

    Args:
        file_path: Path to the target file.
        content: Text content to append.

    Returns:
        Success message with the updated size.
    """
    try:
        # Resolve path (No default extension enforced for append to avoid confusion)
        target_path = _resolve_target_path(file_path)

        # Append content
        with open(target_path, "a", encoding="utf-8") as f:
            f.write(content)

        # Get new size for feedback
        new_size = target_path.stat().st_size
        logger.info(f"file_append: Appended content to {target_path}")

        return build_tool_response(
            True,
            "Content appended successfully.",
            {"path": str(target_path), "total_size": new_size},
        )

    except ValueError as ve:
        return build_tool_response(False, str(ve))
    except Exception as e:
        logger.error(f"file_append error: {e}")
        return build_tool_response(False, f"Failed to append to file: {e}")


def _resolve_target_path(rel_path: str, default_ext: str = None) -> Path:
    """
    Helper to resolve safe paths, ensure parent dirs exist, and handle extensions.
    Raises ValueError if path attempts to escape the base directory.
    """
    base_dir = Path(config.file_base_dir).resolve()

    # strip leading slashes to ensure it treats it as relative
    clean_rel_path = rel_path.lstrip("/\\")
    target_path = (base_dir / clean_rel_path).resolve()

    # 1. Security Check: Path Traversal Prevention
    # Ensures that 'target_path' is actually inside 'base_dir'
    if not target_path.is_relative_to(base_dir):
        raise ValueError(f"Access denied: Path '{rel_path}' is outside the allowed directory.")

    # 2. Extension Handling
    # If the file has no extension and a default is provided, add it.
    if default_ext and not target_path.suffix:
        # Ensure format doesn't duplicate dot (e.g., format=".md" vs "md")
        ext = default_ext if default_ext.startswith(".") else f".{default_ext}"
        target_path = target_path.with_suffix(ext)

    # 3. Directory Creation
    # Automatically create parent folders (mkdir -p)
    if not target_path.parent.exists():
        target_path.parent.mkdir(parents=True, exist_ok=True)

    return target_path
