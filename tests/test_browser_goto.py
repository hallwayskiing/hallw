"""Tests for browser_goto tool."""

import json
from unittest.mock import AsyncMock

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.tools.playwright import goto


@pytest.mark.asyncio
async def test_browser_goto_success(monkeypatch):
    page = AsyncMock()
    page.goto = AsyncMock()

    monkeypatch.setattr(goto, "get_page", AsyncMock(return_value=page))

    data = json.loads(await goto.browser_goto.ainvoke({"page_index": 0, "url": "https://x.com"}))

    assert data["success"] is True
    page.goto.assert_awaited_once()


@pytest.mark.asyncio
async def test_browser_goto_timeout(monkeypatch):
    page = AsyncMock()
    page.goto = AsyncMock(side_effect=PlaywrightTimeoutError("timeout"))

    monkeypatch.setattr(goto, "get_page", AsyncMock(return_value=page))

    data = json.loads(await goto.browser_goto.ainvoke({"page_index": 0, "url": "https://x.com"}))

    assert data["success"] is False
    assert "Timeout" in data["message"]
