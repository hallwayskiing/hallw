import fnmatch
import os
from pathlib import Path
from typing import List

from langchain_core.tools import tool

from hallw.tools import build_tool_response
from hallw.utils import config


@tool
def get_local_file_list(patterns: str = "*") -> str:
    """
    Return newline-separated file paths matching given patterns under current directory.
    Args:
        patterns: Comma-separated glob patterns, e.g. "*.py, *.md"

    Returns:
        line-separated list of matching file paths or error message
    """
    try:
        base = Path(config.file_base_dir).resolve()

        if not base.exists():
            return build_tool_response(False, f"Directory not found: {base}")
        if not base.is_dir():
            return build_tool_response(False, f"Not a directory: {base}")

        # split patterns
        patterns_list: List[str] = [p.strip() for p in patterns.split(",") if p.strip()] or ["*"]

        matches = set()
        cwd = Path.cwd()

        for root, dirs, files in os.walk(base):
            root_path = Path(root)

            dirs[:] = [d for d in dirs if not d.startswith(".") and not d.startswith("_")]

            for fname in files:
                # exclude dotfiles & underscore-files
                if fname.startswith(".") or fname.startswith("_"):
                    continue

                fpath = root_path / fname

                for pat in patterns_list:
                    if fnmatch.fnmatch(fname, pat):
                        try:
                            rel = str(fpath.resolve().relative_to(cwd))
                        except Exception:
                            rel = str(fpath.resolve())
                        matches.add(rel)
                        break

        if not matches:
            return build_tool_response(False, "No files matched.")

        return build_tool_response(True, "Found matching files.", {"files": sorted(matches)})

    except Exception as e:
        return build_tool_response(False, f"Error while listing files: {e}")
