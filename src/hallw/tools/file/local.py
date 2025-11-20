import os
from pathlib import Path
from typing import List

from langchain_core.tools import tool

from hallw.tools import build_tool_response
from hallw.utils import config


@tool
def get_local_file_list(patterns: str = "*") -> str:
    """
    Return newline-separated file paths matching given patterns under the current directory.

    Supports both simple filename patterns (e.g., "*.py") and structural path patterns
    (e.g., "src/hallw/*.py", "**/*.md").

    Args:
        patterns: Comma-separated glob patterns, e.g. "*.py, src/**/*.js"

    Returns:
        Structured response containing the list of matching file paths.
    """
    try:
        # Resolve the base directory from configuration
        base = Path(config.file_read_dir).resolve()
        cwd = Path.cwd()

        if not base.exists():
            return build_tool_response(False, f"Directory not found: {base}")
        if not base.is_dir():
            return build_tool_response(False, f"Not a directory: {base}")

        # Parse patterns
        patterns_list: List[str] = [p.strip() for p in patterns.split(",") if p.strip()] or ["*"]

        matches = set()

        # Walk through the directory tree
        for root, dirs, files in os.walk(base):
            root_path = Path(root)

            # Optimization: Modify 'dirs' in-place to skip hidden/system directories
            # This prevents os.walk from entering .git, .venv, __pycache__, etc.
            dirs[:] = [d for d in dirs if not d.startswith(".") and not d.startswith("_")]

            for fname in files:
                # Skip hidden files and private files (starting with . or _)
                if fname.startswith(".") or fname.startswith("_"):
                    continue

                full_path = root_path / fname

                try:
                    # Calculate the path relative to the base root for matching.
                    # e.g., D:/proj/src/main.py -> src/main.py
                    rel_path_obj = full_path.relative_to(base)
                except ValueError:
                    continue

                # Check against all patterns
                for pat in patterns_list:
                    # Path.match() is smart:
                    # "*.py" matches "src/tools.py" (filename match)
                    # "src/*.py" matches "src/tools.py" (path match)
                    if rel_path_obj.match(pat):
                        try:
                            # Return path relative to CWD for better readability by the LLM
                            final_rel = str(full_path.resolve().relative_to(cwd))
                        except Exception:
                            # Fallback to absolute path if outside CWD
                            final_rel = str(full_path.resolve())

                        matches.add(final_rel)
                        break

        if not matches:
            return build_tool_response(False, "No files matched.")

        return build_tool_response(True, "Found matching files.", {"files": sorted(matches)})

    except Exception as e:
        return build_tool_response(False, f"Error while listing files: {e}")
