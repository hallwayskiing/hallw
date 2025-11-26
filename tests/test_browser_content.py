"""Tests for browser_get_content tool."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from hallw.tools.playwright import content
from hallw.utils import config


@pytest.mark.asyncio
async def test_browser_get_content_segments(monkeypatch):
    page = _build_page_with_content("abcdef12345")
    monkeypatch.setattr(config, "max_page_content_chars", 5)
    monkeypatch.setattr(content, "get_page", AsyncMock(return_value=page))

    data = json.loads(await content.browser_get_content.ainvoke({"page_index": 0, "segment": 1}))

    assert data["success"] is True
    assert data["data"]["content"] == "f1234"
    assert data["data"]["total_segments"] == 3


@pytest.mark.asyncio
async def test_browser_get_content_out_of_range(monkeypatch):
    page = _build_page_with_content("abc")
    monkeypatch.setattr(config, "max_page_content_chars", 2)
    monkeypatch.setattr(content, "get_page", AsyncMock(return_value=page))

    data = json.loads(await content.browser_get_content.ainvoke({"page_index": 0, "segment": 2}))

    assert data["success"] is False
    assert "out of range" in data["message"]


# Ensure trailing whitespace trimmed so initial selector content is considered empty in None case


def _build_page_with_content(content_text: str):
    page = AsyncMock()
    locator = AsyncMock()
    locator.count = AsyncMock(return_value=1)
    locator.nth = MagicMock(return_value=locator)
    locator.inner_text = AsyncMock(return_value=content_text)
    page.locator = MagicMock(return_value=locator)
    return page
