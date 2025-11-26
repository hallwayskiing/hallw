"""Tests for get_local_file_list tool."""

import json

from hallw.tools.file.local import get_local_file_list
from hallw.utils import config


def test_lists_matching_files(workspace_dir):
    (workspace_dir / "a.txt").write_text("a")
    (workspace_dir / "b.md").write_text("b")
    (workspace_dir / ".hidden").write_text("x")
    nested = workspace_dir / "sub"
    nested.mkdir()
    (nested / "c.txt").write_text("c")

    data = json.loads(get_local_file_list.invoke({"patterns": "*.txt"}))

    assert data["success"] is True
    files = data["data"]["files"]
    assert any(f.endswith("a.txt") for f in files)
    assert any(f.endswith("sub\\c.txt") or f.endswith("sub/c.txt") for f in files)
    assert not any("hidden" in f for f in files)


def test_multiple_patterns(workspace_dir):
    (workspace_dir / "match.py").write_text("x")
    (workspace_dir / "skip.txt").write_text("y")

    data = json.loads(get_local_file_list.invoke({"patterns": "*.py, *.md"}))

    assert data["success"] is True
    assert any(f.endswith("match.py") for f in data["data"]["files"])
    assert not any(f.endswith("skip.txt") for f in data["data"]["files"])


def test_no_matches_returns_error(workspace_dir):
    data = json.loads(get_local_file_list.invoke({"patterns": "*.zzz"}))

    assert data["success"] is False
    assert "No files matched" in data["message"]


def test_missing_directory(monkeypatch):
    monkeypatch.setattr(config, "file_read_dir", "Z:/does/not/exist")

    data = json.loads(get_local_file_list.invoke({}))

    assert data["success"] is False
    assert "Directory not found" in data["message"]
