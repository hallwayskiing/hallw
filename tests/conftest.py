"""Pytest configuration and fixtures."""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from hallw.tools.playwright.playwright_state import set_page


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for test files."""
    return tmp_path


@pytest.fixture
def sample_text_file(temp_dir):
    """Create a sample text file for testing."""
    file_path = temp_dir / "test.txt"
    file_path.write_text("This is a test file.\nLine 2\nLine 3")
    return file_path


@pytest.fixture
def sample_json_file(temp_dir):
    """Create a sample JSON file for testing."""
    import json

    file_path = temp_dir / "test.json"
    data = {"name": "test", "value": 123, "items": [1, 2, 3]}
    file_path.write_text(json.dumps(data))
    return file_path


@pytest.fixture
def mock_page():
    """Create a mock Playwright page."""
    page = AsyncMock()
    page.goto = AsyncMock()
    page.get_by_role = Mock(return_value=AsyncMock())
    page.locator = Mock(return_value=AsyncMock())
    page.query_selector = AsyncMock(return_value=None)
    page.wait_for_selector = AsyncMock()
    page.accessibility = AsyncMock()
    return page


@pytest.fixture(autouse=True)
def reset_config(monkeypatch):
    """Reset environment variables before each test."""
    # Clear any test-specific env vars
    test_env = {k: v for k, v in os.environ.items() if not k.startswith("HALLW_TEST_")}
    for key in os.environ.keys():
        if key.startswith("MODEL_") or key.startswith("PW_") or key.startswith("FILE_"):
            monkeypatch.delenv(key, raising=False)


@pytest.fixture(autouse=True)
def mock_playwright_stealth():
    """Avoid running real Stealth logic when tests call set_page."""
    with patch("hallw.tools.playwright.playwright_state.Stealth") as stealth_cls:
        stealth = AsyncMock()
        stealth.apply_stealth_async = AsyncMock()
        stealth_cls.return_value = stealth
        yield


@pytest.fixture
def page_context():
    """Async context manager that sets/clears the global Playwright page."""

    @asynccontextmanager
    async def _ctx(page):
        await set_page(page)
        try:
            yield page
        finally:
            await set_page(None)

    return _ctx
