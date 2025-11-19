"""Tests for get_local_file_list tool."""

import json
from pathlib import Path

import pytest

from hallw.tools.file.local import get_local_file_list
from hallw.utils.config_mgr import config


@pytest.fixture
def temp_file_dir(tmp_path, monkeypatch):
    """Set up temporary directory for file operations."""
    monkeypatch.setattr(config, "file_base_dir", str(tmp_path))
    return tmp_path


def test_get_local_file_list_all_files(temp_file_dir):
    """Test getting all files with default pattern."""
    # Create test files
    (temp_file_dir / "test1.txt").write_text("content1")
    (temp_file_dir / "test2.md").write_text("content2")
    (temp_file_dir / "test3.py").write_text("content3")

    result = get_local_file_list.invoke({})
    data = json.loads(result)

    assert data["success"] is True
    assert "Found matching files" in data["message"]
    assert len(data["data"]["files"]) >= 3
    assert any("test1.txt" in f for f in data["data"]["files"])
    assert any("test2.md" in f for f in data["data"]["files"])
    assert any("test3.py" in f for f in data["data"]["files"])


def test_get_local_file_list_with_pattern(temp_file_dir):
    """Test getting files with specific pattern."""
    # Create test files
    (temp_file_dir / "test1.txt").write_text("content1")
    (temp_file_dir / "test2.md").write_text("content2")
    (temp_file_dir / "test3.py").write_text("content3")

    result = get_local_file_list.invoke({"patterns": "*.txt"})
    data = json.loads(result)

    assert data["success"] is True
    files = data["data"]["files"]
    assert any("test1.txt" in f for f in files)
    # Should not include .md or .py files
    assert not any("test2.md" in f for f in files)
    assert not any("test3.py" in f for f in files)


def test_get_local_file_list_multiple_patterns(temp_file_dir):
    """Test getting files with multiple patterns."""
    # Create test files
    (temp_file_dir / "test1.txt").write_text("content1")
    (temp_file_dir / "test2.md").write_text("content2")
    (temp_file_dir / "test3.py").write_text("content3")

    result = get_local_file_list.invoke({"patterns": "*.txt, *.md"})
    data = json.loads(result)

    assert data["success"] is True
    files = data["data"]["files"]
    assert any("test1.txt" in f for f in files)
    assert any("test2.md" in f for f in files)
    assert not any("test3.py" in f for f in files)


def test_get_local_file_list_no_matches(temp_file_dir):
    """Test getting files with pattern that matches nothing."""
    result = get_local_file_list.invoke({"patterns": "*.nonexistent"})
    data = json.loads(result)

    assert data["success"] is False
    assert "No files matched" in data["message"]


def test_get_local_file_list_excludes_dotfiles(temp_file_dir):
    """Test that dotfiles are excluded."""
    # Create test files including dotfiles
    (temp_file_dir / "visible.txt").write_text("content")
    (temp_file_dir / ".hidden.txt").write_text("content")
    (temp_file_dir / "_private.txt").write_text("content")

    result = get_local_file_list.invoke({"patterns": "*.txt"})
    data = json.loads(result)

    assert data["success"] is True
    files = data["data"]["files"]
    assert any("visible.txt" in f for f in files)
    assert not any(".hidden.txt" in f for f in files)
    assert not any("_private.txt" in f for f in files)


def test_get_local_file_list_nested_directory(temp_file_dir):
    """Test getting files in nested directories."""
    # Create nested structure
    subdir = temp_file_dir / "subdir"
    subdir.mkdir()
    (subdir / "nested.txt").write_text("content")

    result = get_local_file_list.invoke({"patterns": "*.txt"})
    data = json.loads(result)

    assert data["success"] is True
    assert any("nested.txt" in f for f in data["data"]["files"])


def test_get_local_file_list_nonexistent_directory(monkeypatch):
    """Test getting files from non-existent directory."""
    monkeypatch.setattr(config, "file_base_dir", "/nonexistent/path")

    result = get_local_file_list.invoke({})
    data = json.loads(result)

    assert data["success"] is False
    assert "Directory not found" in data["message"]
