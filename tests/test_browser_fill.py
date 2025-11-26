"""Tests for browser_fill tool."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.tools.playwright import fill
from hallw.utils import config


@pytest.mark.asyncio
async def test_browser_fill_success(monkeypatch):
    locator = _build_locator(count=1, fill_result=None)
    page = AsyncMock()
    page.get_by_role = MagicMock(return_value=locator)

    monkeypatch.setattr(fill, "get_page", AsyncMock(return_value=page))

    data = json.loads(
        await fill.browser_fill.ainvoke(
            {"page_index": 0, "role": "textbox", "name": "q", "text": "hello"}
        )
    )

    assert data["success"] is True
    locator.fill.assert_awaited_once_with("hello", timeout=config.pw_click_timeout)


@pytest.mark.asyncio
async def test_browser_fill_multiple(monkeypatch):
    locator = _build_locator(count=2)
    page = AsyncMock()
    page.get_by_role = MagicMock(return_value=locator)

    monkeypatch.setattr(fill, "get_page", AsyncMock(return_value=page))

    data = json.loads(
        await fill.browser_fill.ainvoke(
            {"page_index": 0, "role": "textbox", "name": "q", "text": "hello"}
        )
    )

    assert data["success"] is False
    assert "Multiple" in data["message"]


@pytest.mark.asyncio
async def test_browser_fill_timeout(monkeypatch):
    locator = _build_locator(count=1, fill_result=PlaywrightTimeoutError("timeout"))
    page = AsyncMock()
    page.get_by_role = MagicMock(return_value=locator)

    monkeypatch.setattr(fill, "get_page", AsyncMock(return_value=page))

    data = json.loads(
        await fill.browser_fill.ainvoke(
            {"page_index": 0, "role": "textbox", "name": "q", "text": "hello"}
        )
    )

    assert data["success"] is False
    assert "Timeout" in data["message"]


def _build_locator(count=1, fill_result=None):
    locator = AsyncMock()
    locator.count = AsyncMock(return_value=count)
    locator.nth = MagicMock(return_value=locator)
    if fill_result is not None:
        locator.fill = AsyncMock(side_effect=fill_result)
    else:
        locator.fill = AsyncMock()
    return locator
