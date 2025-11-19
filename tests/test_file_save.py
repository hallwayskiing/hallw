"""Tests for file_save and file_append tools."""

import json

import pytest

from hallw.tools.file.save import file_append, file_save
from hallw.utils.config_mgr import config


@pytest.fixture
def temp_file_dir(tmp_path, monkeypatch):
    """Set up temporary directory for file operations."""
    monkeypatch.setattr(config, "file_base_dir", str(tmp_path))
    return tmp_path


def test_file_save_success(temp_file_dir):
    """Test saving a file successfully."""
    content = "This is test content\nLine 2"
    result = file_save.invoke({"file_path": "test.md", "content": content, "format": "md"})
    data = json.loads(result)

    assert data["success"] is True
    assert "File saved successfully" in data["message"]
    assert data["data"]["size"] == len(content)

    # Verify file was created
    saved_file = temp_file_dir / "test.md"
    assert saved_file.exists()
    assert saved_file.read_text() == content


def test_file_save_without_extension(temp_file_dir):
    """Test saving a file without extension (should add .md)."""
    content = "Test content"
    result = file_save.invoke({"file_path": "testfile", "content": content})
    data = json.loads(result)

    assert data["success"] is True

    # Verify file was created with .md extension
    saved_file = temp_file_dir / "testfile.md"
    assert saved_file.exists()
    assert saved_file.read_text() == content


def test_file_save_nested_path(temp_file_dir):
    """Test saving a file in a nested directory."""
    content = "Nested content"
    result = file_save.invoke({"file_path": "subdir/nested.md", "content": content})
    data = json.loads(result)

    assert data["success"] is True

    # Verify file was created in nested directory
    saved_file = temp_file_dir / "subdir" / "nested.md"
    assert saved_file.exists()
    assert saved_file.read_text() == content


def test_file_save_different_format(temp_file_dir):
    """Test saving a file with different format."""
    content = "print('Hello, World!')"
    result = file_save.invoke({"file_path": "script.py", "content": content, "format": "py"})
    data = json.loads(result)

    assert data["success"] is True

    saved_file = temp_file_dir / "script.py"
    assert saved_file.exists()
    assert saved_file.read_text() == content


def test_file_append_to_existing_file(temp_file_dir):
    """Test appending to an existing file."""
    # Create initial file
    initial_file = temp_file_dir / "append_test.md"
    initial_file.write_text("Initial content\n")

    # Append content
    append_content = "Appended content"
    result = file_append.invoke({"file_path": "append_test.md", "content": append_content})
    data = json.loads(result)

    assert data["success"] is True

    # Verify content was appended
    final_content = initial_file.read_text()
    assert "Initial content" in final_content
    assert "Appended content" in final_content


def test_file_append_to_new_file(temp_file_dir):
    """Test appending to a new file (should create it)."""
    append_content = "New file content"
    result = file_append.invoke({"file_path": "new_file.md", "content": append_content})
    data = json.loads(result)

    assert data["success"] is True

    # Verify file was created
    new_file = temp_file_dir / "new_file.md"
    assert new_file.exists()
    assert new_file.read_text() == append_content


def test_file_append_without_extension(temp_file_dir):
    """Test appending to a file without extension (should add .md)."""
    append_content = "Content"
    result = file_append.invoke({"file_path": "appendfile", "content": append_content})
    data = json.loads(result)

    assert data["success"] is True

    # Verify file was created with .md extension
    new_file = temp_file_dir / "appendfile.md"
    assert new_file.exists()
