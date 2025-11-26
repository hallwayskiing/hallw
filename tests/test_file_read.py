"""Tests for file_read tool."""

import json

from hallw.tools.file.read import file_read
from hallw.utils import config


def test_reads_text_file(workspace_dir):
    target = workspace_dir / "sample.txt"
    target.write_text("Hello\nWorld")

    data = json.loads(file_read.invoke({"file_path": "sample.txt"}))

    assert data["success"] is True
    assert "Hello" in data["data"]["content"]
    assert data["data"]["path"].endswith("sample.txt")


def test_reads_json_with_pretty_format(workspace_dir):
    target = workspace_dir / "data.json"
    target.write_text('{"a":1,"b":2}')

    data = json.loads(file_read.invoke({"file_path": "data.json"}))

    assert data["success"] is True
    assert '"a": 1' in data["data"]["content"]


def test_truncates_when_over_limit(workspace_dir, monkeypatch):
    monkeypatch.setattr(config, "file_max_read_chars", 5)
    target = workspace_dir / "long.txt"
    target.write_text("0123456789")

    data = json.loads(file_read.invoke({"file_path": "long.txt"}))

    assert data["success"] is True
    assert "truncated" in data["data"]["content"]


def test_rejects_binary_file(workspace_dir):
    target = workspace_dir / "binary.bin"
    target.write_bytes(b"\x00\x01\x02")

    data = json.loads(file_read.invoke({"file_path": "binary.bin"}))

    assert data["success"] is False
    assert "binary file" in data["message"]


def test_handles_missing_file(workspace_dir):
    data = json.loads(file_read.invoke({"file_path": "missing.txt"}))

    assert data["success"] is False
    assert "not found" in data["message"].lower()
