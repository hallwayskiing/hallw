"""Tests for file_read tool."""

import json

import pytest

from hallw.tools.file.read import file_read
from hallw.utils.config_mgr import config


@pytest.fixture
def temp_file_dir(tmp_path, monkeypatch):
    """Set up temporary directory for file operations."""
    monkeypatch.setattr(config, "file_base_dir", str(tmp_path))
    monkeypatch.setattr(config, "file_max_read_chars", 10000)
    return tmp_path


def test_file_read_text_file(temp_file_dir):
    """Test reading a text file."""
    test_file = temp_file_dir / "test.txt"
    test_file.write_text("Hello, World!\nThis is a test file.")

    result = file_read.invoke({"file_path": "test.txt"})
    data = json.loads(result)

    assert data["success"] is True
    assert "File content retrieved" in data["message"]
    assert "Hello, World!" in data["data"]["content"]
    assert "This is a test file" in data["data"]["content"]


def test_file_read_json_file(temp_file_dir):
    """Test reading a JSON file."""
    test_file = temp_file_dir / "test.json"
    test_data = {"name": "test", "value": 123, "items": [1, 2, 3]}
    import json as json_module

    test_file.write_text(json_module.dumps(test_data))

    result = file_read.invoke({"file_path": "test.json"})
    data = json.loads(result)

    assert data["success"] is True
    assert "test" in data["data"]["content"]
    assert "123" in data["data"]["content"]


def test_file_read_markdown_file(temp_file_dir):
    """Test reading a markdown file."""
    test_file = temp_file_dir / "test.md"
    test_file.write_text("# Title\n\nThis is markdown content.")

    result = file_read.invoke({"file_path": "test.md"})
    data = json.loads(result)

    assert data["success"] is True
    assert "Title" in data["data"]["content"]
    assert "markdown content" in data["data"]["content"]


def test_file_read_csv_file(temp_file_dir):
    """Test reading a CSV file."""
    test_file = temp_file_dir / "test.csv"
    test_file.write_text("name,age,city\nJohn,30,NYC\nJane,25,LA")

    result = file_read.invoke({"file_path": "test.csv"})
    data = json.loads(result)

    assert data["success"] is True
    assert "name" in data["data"]["content"]
    assert "John" in data["data"]["content"]


def test_file_read_nonexistent_file(temp_file_dir):
    """Test reading a non-existent file."""
    result = file_read.invoke({"file_path": "nonexistent.txt"})
    data = json.loads(result)

    assert data["success"] is False
    assert "File not found" in data["message"]


def test_file_read_unsupported_format(temp_file_dir):
    """Test reading an unsupported file format."""
    test_file = temp_file_dir / "test.xyz"
    test_file.write_text("some content")

    result = file_read.invoke({"file_path": "test.xyz"})
    data = json.loads(result)

    assert data["success"] is False
    assert "Unsupported file type" in data["message"]


def test_file_read_directory(temp_file_dir):
    """Test reading a directory (should fail)."""
    subdir = temp_file_dir / "subdir"
    subdir.mkdir()

    result = file_read.invoke({"file_path": "subdir"})
    data = json.loads(result)

    assert data["success"] is False
    assert "not a file" in data["message"].lower()


def test_file_read_truncation(temp_file_dir, monkeypatch):
    """Test file content truncation when exceeding max chars."""
    monkeypatch.setattr(config, "file_max_read_chars", 10)
    test_file = temp_file_dir / "long.txt"
    test_file.write_text("This is a very long file content that should be truncated")

    result = file_read.invoke({"file_path": "long.txt"})
    data = json.loads(result)

    assert data["success"] is True
    assert "truncated" in data["data"]["content"].lower()
    assert (
        len(data["data"]["content"]) < len(test_file.read_text()) + 50
    )  # Allow for truncation message
