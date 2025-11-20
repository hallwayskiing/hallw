import re
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
    Fully robust version:
    - Validates base_dir (config.file_save_dir)
    - Secures path traversal
    - Rejects illegal filename characters (Windows + POSIX safe)
    - Handles missing/invalid extensions cleanly
    - Auto-create directory tree
    """
    # 0. Load base directory
    base_dir_raw = getattr(config, "file_save_dir", None)
    if not base_dir_raw:
        raise ValueError("config.file_save_dir is not set or empty.")

    base_dir = Path(base_dir_raw).expanduser().resolve()

    # 1. base_dir validation
    if base_dir.exists() and not base_dir.is_dir():
        raise ValueError(f"Configured file_save_dir '{base_dir}' is not a directory.")

    # Auto-create save directory
    base_dir.mkdir(parents=True, exist_ok=True)

    # 2. Strip leading slashes (force relative)
    clean_rel_path = rel_path.lstrip("/\\").strip()

    if not clean_rel_path:
        raise ValueError("Relative file path must not be empty or only slashes.")

    # 3. Illegal character check (Windows forbidden set, also safe for Linux)
    #    <>:"/\|?* are dangerous or invalid across platforms
    illegal_chars = r'[<>:"/\\|?*\x00-\x1F]'
    if re.search(illegal_chars, Path(clean_rel_path).name):
        raise ValueError(
            f"Path '{clean_rel_path}' contains illegal characters "
            '(<>:"/\\|?* or control chars are not allowed).'
        )

    # 4. Build absolute path
    target_path = (base_dir / clean_rel_path).resolve()

    # 5. Path traversal protection
    if not target_path.is_relative_to(base_dir):
        raise ValueError(f"Access denied: Path '{rel_path}' escapes the save directory.")

    # 6. Extension normalization
    # Reject paths that end with a bare dot ("file.")
    if target_path.name.endswith("."):
        raise ValueError("File name cannot end with a bare '.'")

    # Apply default extension only when no valid suffix
    if default_ext and target_path.suffix == "":
        ext = default_ext if default_ext.startswith(".") else f".{default_ext}"
        target_path = target_path.with_suffix(ext)

    # 7. Create parent directories for the final path
    target_path.parent.mkdir(parents=True, exist_ok=True)

    return target_path
