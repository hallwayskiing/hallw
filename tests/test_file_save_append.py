"""Tests for file_save and file_append tools."""

import json

import pytest

from hallw.tools.file.save import file_append, file_save


def test_file_save_adds_default_extension(workspace_dir):
    content = "hello world"

    result = file_save.invoke({"file_path": "note", "content": content})
    data = json.loads(result)

    assert data["success"] is True
    saved = workspace_dir / "note.md"
    assert saved.read_text() == content
    assert data["data"]["size"] == len(content)


def test_file_save_nested_path_creates_parents(workspace_dir):
    content = "nested"

    result = file_save.invoke({"file_path": "a/b/c.txt", "content": content, "format": "txt"})
    data = json.loads(result)

    assert data["success"] is True
    saved = workspace_dir / "a" / "b" / "c.txt"
    assert saved.exists()
    assert saved.read_text() == content


@pytest.mark.parametrize(
    "file_path, expected_msg",
    [
        ("../escape.txt", "escapes the save directory"),
        ("bad|name.txt", "illegal characters"),
    ],
)
def test_file_save_rejects_invalid_paths(workspace_dir, file_path, expected_msg):
    result = file_save.invoke({"file_path": file_path, "content": "x"})
    data = json.loads(result)

    assert data["success"] is False
    assert expected_msg in data["message"]


def test_file_append_updates_existing_file(workspace_dir):
    target = workspace_dir / "log.txt"
    target.write_text("first\n")

    append = "second\n"
    result = file_append.invoke({"file_path": "log.txt", "content": append})
    data = json.loads(result)

    assert data["success"] is True
    assert "total_size" in data["data"]
    assert target.read_text() == "first\nsecond\n"


def test_file_append_creates_when_missing(workspace_dir):
    result = file_append.invoke({"file_path": "new.log", "content": "content"})
    data = json.loads(result)

    assert data["success"] is True
    created = workspace_dir / "new.log"
    assert created.exists()
    assert created.read_text() == "content"
