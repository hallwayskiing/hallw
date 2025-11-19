"""Tests for the browser_fill tool."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.tools.playwright.fill import browser_fill


@pytest.mark.asyncio
async def test_browser_fill_success(page_context):
    page = AsyncMock()
    locator = AsyncMock()
    locator.count = AsyncMock(return_value=1)
    locator.fill = AsyncMock()
    page.get_by_role = MagicMock(return_value=locator)

    payload = {"role": "textbox", "name": "username", "text": "testuser"}
    async with page_context(page):
        result = await browser_fill.ainvoke(payload)

    data = json.loads(result)
    assert data["success"] is True
    assert "Input filled successfully" in data["message"]
    locator.fill.assert_called_once_with("testuser", timeout=6000)


@pytest.mark.asyncio
async def test_browser_fill_element_not_found(page_context):
    page = AsyncMock()
    locator = AsyncMock()
    locator.count = AsyncMock(return_value=0)
    page.get_by_role = MagicMock(return_value=locator)

    async with page_context(page):
        result = await browser_fill.ainvoke({"role": "textbox", "name": "missing", "text": "x"})

    data = json.loads(result)
    assert data["success"] is False
    assert "No input field found" in data["message"]


@pytest.mark.asyncio
async def test_browser_fill_multiple_elements(page_context):
    page = AsyncMock()
    locator = AsyncMock()
    locator.count = AsyncMock(return_value=2)
    page.get_by_role = MagicMock(return_value=locator)

    async with page_context(page):
        result = await browser_fill.ainvoke({"role": "textbox", "name": "ambiguous", "text": "x"})

    data = json.loads(result)
    assert data["success"] is False
    assert "Multiple" in data["message"]


@pytest.mark.asyncio
async def test_browser_fill_timeout(page_context):
    page = AsyncMock()
    locator = AsyncMock()
    locator.count = AsyncMock(return_value=1)
    locator.fill = AsyncMock(side_effect=PlaywrightTimeoutError("Timeout"))
    page.get_by_role = MagicMock(return_value=locator)

    async with page_context(page):
        result = await browser_fill.ainvoke(
            {"role": "textbox", "name": "username", "text": "testuser"}
        )

    data = json.loads(result)
    assert data["success"] is False
    assert "Timeout" in data["message"]
