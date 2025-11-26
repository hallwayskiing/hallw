"""Tests for browser_click tool."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.tools.playwright import click


@pytest.mark.asyncio
async def test_browser_click_success(monkeypatch):
    locator = _build_locator(count=1, click_result=None)
    page = AsyncMock()
    page.get_by_role = MagicMock(return_value=locator)

    monkeypatch.setattr(click, "get_page", AsyncMock(return_value=page))

    data = json.loads(
        await click.browser_click.ainvoke({"page_index": 0, "role": "button", "name": "OK"})
    )

    assert data["success"] is True
    locator.click.assert_awaited_once()


@pytest.mark.asyncio
async def test_browser_click_not_found(monkeypatch):
    locator = _build_locator(count=0)
    page = AsyncMock()
    page.get_by_role = MagicMock(return_value=locator)

    monkeypatch.setattr(click, "get_page", AsyncMock(return_value=page))

    data = json.loads(
        await click.browser_click.ainvoke({"page_index": 0, "role": "button", "name": "OK"})
    )

    assert data["success"] is False
    assert "No 'button' found" in data["message"]


@pytest.mark.asyncio
async def test_browser_click_timeout(monkeypatch):
    locator = _build_locator(count=1, click_result=PlaywrightTimeoutError("timeout"))
    page = AsyncMock()
    page.get_by_role = MagicMock(return_value=locator)

    monkeypatch.setattr(click, "get_page", AsyncMock(return_value=page))

    data = json.loads(
        await click.browser_click.ainvoke({"page_index": 0, "role": "button", "name": "OK"})
    )

    assert data["success"] is False
    assert "Timeout" in data["message"]


def _build_locator(count=1, click_result=None):
    locator = AsyncMock()
    locator.count = AsyncMock(return_value=count)
    locator.first = locator
    locator.nth = MagicMock(return_value=locator)
    if click_result is not None:
        locator.click = AsyncMock(side_effect=click_result)
    else:
        locator.click = AsyncMock()
    return locator
