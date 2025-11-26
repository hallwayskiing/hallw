"""Pytest configuration and fixtures for tool tests."""

import pytest

from hallw.utils import config


@pytest.fixture
def workspace_dir(tmp_path, monkeypatch):
    """Point file read/save locations to an isolated temp directory."""
    monkeypatch.setattr(config, "file_read_dir", str(tmp_path))
    monkeypatch.setattr(config, "file_save_dir", str(tmp_path))
    monkeypatch.setattr(config, "file_max_read_chars", 5000)
    return tmp_path


@pytest.fixture
def sample_text_file(workspace_dir):
    """Create a sample text file for tests."""
    file_path = workspace_dir / "test.txt"
    file_path.write_text("This is a test file.\nLine 2\nLine 3")
    return file_path


@pytest.fixture
def sample_json_file(workspace_dir):
    """Create a sample JSON file for tests."""
    import json

    file_path = workspace_dir / "test.json"
    data = {"name": "test", "value": 123, "items": [1, 2, 3]}
    file_path.write_text(json.dumps(data))
    return file_path
