"""Tests for the browser_get_content tool."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from hallw.tools.playwright.content import browser_get_content


@pytest.mark.asyncio
async def test_browser_get_content_success(page_context):
    page = AsyncMock()
    locator = AsyncMock()
    locator.count = AsyncMock(return_value=1)
    locator.nth = MagicMock(return_value=locator)
    locator.inner_text = AsyncMock(return_value="Test page content here")
    page.locator = MagicMock(return_value=locator)

    async with page_context(page):
        result = await browser_get_content.ainvoke({"segment": 0})

    data = json.loads(result)
    assert data["success"] is True
    assert data["data"]["segment"] == 0
    assert "Test page content" in data["data"]["content"]


@pytest.mark.asyncio
async def test_browser_get_content_segment_1(page_context):
    page = AsyncMock()
    locator = AsyncMock()
    locator.count = AsyncMock(return_value=1)
    locator.nth = MagicMock(return_value=locator)
    locator.inner_text = AsyncMock(return_value="A" * 3000)
    page.locator = MagicMock(return_value=locator)

    async with page_context(page):
        result = await browser_get_content.ainvoke({"segment": 1})

    data = json.loads(result)
    assert data["success"] is True
    assert data["data"]["segment"] == 1
    assert data["data"]["total_segments"] >= 2


@pytest.mark.asyncio
async def test_browser_get_content_empty_page(page_context):
    page = AsyncMock()
    locator = AsyncMock()
    locator.count = AsyncMock(return_value=1)
    locator.nth = MagicMock(return_value=locator)
    locator.inner_text = AsyncMock(return_value="   ")
    page.locator = MagicMock(return_value=locator)

    async with page_context(page):
        result = await browser_get_content.ainvoke({"segment": 0})

    data = json.loads(result)
    assert data["success"] is False
    assert "The page is empty" in data["message"]


@pytest.mark.asyncio
async def test_browser_get_content_negative_segment(page_context):
    page = AsyncMock()
    locator = AsyncMock()
    locator.count = AsyncMock(return_value=1)
    locator.nth = MagicMock(return_value=locator)
    locator.inner_text = AsyncMock(return_value="Content")
    page.locator = MagicMock(return_value=locator)

    async with page_context(page):
        result = await browser_get_content.ainvoke({"segment": -1})

    data = json.loads(result)
    assert data["success"] is True
    assert data["data"]["segment"] == 0
