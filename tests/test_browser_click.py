"""Tests for the browser_click tool."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.tools.playwright.click import browser_click


@pytest.mark.asyncio
async def test_browser_click_success(page_context):
    page = AsyncMock()
    locator = AsyncMock()
    locator.count = AsyncMock(return_value=1)
    locator.first = MagicMock()
    locator.first.click = AsyncMock()
    page.get_by_role = MagicMock(return_value=locator)

    async with page_context(page):
        result = await browser_click.ainvoke({"role": "button", "name": "Submit"})

    data = json.loads(result)
    assert data["success"] is True
    assert "Element clicked successfully" in data["message"]
    assert data["data"]["name"] == "Submit"


@pytest.mark.asyncio
async def test_browser_click_element_not_found(page_context):
    page = AsyncMock()
    locator = AsyncMock()
    locator.count = AsyncMock(return_value=0)
    page.get_by_role = MagicMock(return_value=locator)

    async with page_context(page):
        result = await browser_click.ainvoke({"role": "button", "name": "Missing"})

    data = json.loads(result)
    assert data["success"] is False
    assert "No 'button' found" in data["message"]


@pytest.mark.asyncio
async def test_browser_click_timeout(page_context):
    page = AsyncMock()
    locator = AsyncMock()
    locator.count = AsyncMock(return_value=1)
    locator.first = MagicMock()
    locator.first.click = AsyncMock(side_effect=PlaywrightTimeoutError("Timeout"))
    page.get_by_role = MagicMock(return_value=locator)

    async with page_context(page):
        result = await browser_click.ainvoke({"role": "button", "name": "Submit"})

    data = json.loads(result)
    assert data["success"] is False
    assert "Timeout" in data["message"]
