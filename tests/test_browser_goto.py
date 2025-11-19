"""Tests for the browser_goto tool."""

import json
from unittest.mock import AsyncMock

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.tools.playwright.goto import browser_goto


@pytest.mark.asyncio
async def test_browser_goto_success(page_context):
    page = AsyncMock()
    page.goto = AsyncMock(return_value=None)

    async with page_context(page):
        result = await browser_goto.ainvoke({"url": "https://example.com"})

    data = json.loads(result)
    assert data["success"] is True
    assert "Navigation successful" in data["message"]
    page.goto.assert_called_once_with(
        "https://example.com", wait_until="domcontentloaded", timeout=10000
    )


@pytest.mark.asyncio
async def test_browser_goto_timeout(page_context):
    page = AsyncMock()
    page.goto = AsyncMock(side_effect=PlaywrightTimeoutError("Timeout"))

    async with page_context(page):
        result = await browser_goto.ainvoke({"url": "https://example.com"})

    data = json.loads(result)
    assert data["success"] is False
    assert "Timeout" in data["message"]
