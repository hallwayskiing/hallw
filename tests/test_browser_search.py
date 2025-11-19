"""Tests for the browser_search tool."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from hallw.tools.playwright.search import browser_search


@pytest.mark.asyncio
async def test_browser_search_success(page_context):
    page = AsyncMock()
    page.goto = AsyncMock()
    page.query_selector = AsyncMock(return_value=None)
    page.wait_for_selector = AsyncMock()

    search_container = AsyncMock()
    link_locators = AsyncMock()
    link_locators.count = AsyncMock(return_value=2)

    link1 = AsyncMock()
    title1 = AsyncMock()
    title1.count = AsyncMock(return_value=1)
    title1.inner_text = AsyncMock(return_value="Test Result 1")
    link1.locator = MagicMock(return_value=title1)
    link1.get_attribute = AsyncMock(return_value="https://example.com/1")

    link2 = AsyncMock()
    title2 = AsyncMock()
    title2.count = AsyncMock(return_value=1)
    title2.inner_text = AsyncMock(return_value="Test Result 2")
    link2.locator = MagicMock(return_value=title2)
    link2.get_attribute = AsyncMock(return_value="https://example.com/2")

    link_locators.nth = MagicMock(side_effect=[link1, link2])
    search_container.locator = MagicMock(return_value=link_locators)
    page.locator = MagicMock(return_value=search_container)

    async with page_context(page):
        result = await browser_search.ainvoke({"query": "test query"})

    data = json.loads(result)
    assert data["success"] is True
    assert len(data["data"]["results"]) == 2


@pytest.mark.asyncio
async def test_browser_search_no_results(page_context):
    page = AsyncMock()
    page.goto = AsyncMock()
    page.query_selector = AsyncMock(return_value=None)
    page.wait_for_selector = AsyncMock()

    search_container = AsyncMock()
    link_locators = AsyncMock()
    link_locators.count = AsyncMock(return_value=0)
    search_container.locator = MagicMock(return_value=link_locators)
    page.locator = MagicMock(return_value=search_container)

    async with page_context(page):
        result = await browser_search.ainvoke({"query": "test query"})

    data = json.loads(result)
    assert data["success"] is False
    assert "No valid search results found" in data["message"]


@pytest.mark.asyncio
async def test_browser_search_captcha_detected(page_context):
    page = AsyncMock()
    page.goto = AsyncMock()
    page.query_selector = AsyncMock(side_effect=[AsyncMock(), None])
    page.wait_for_selector = AsyncMock()

    search_container = AsyncMock()
    link_locators = AsyncMock()
    link_locators.count = AsyncMock(return_value=1)

    link = AsyncMock()
    title = AsyncMock()
    title.count = AsyncMock(return_value=1)
    title.inner_text = AsyncMock(return_value="Result")
    link.locator = MagicMock(return_value=title)
    link.get_attribute = AsyncMock(return_value="https://example.com")

    link_locators.nth = MagicMock(return_value=link)
    search_container.locator = MagicMock(return_value=link_locators)
    page.locator = MagicMock(return_value=search_container)

    async with page_context(page):
        await browser_search.ainvoke({"query": "test query"})

    page.wait_for_selector.assert_called()


@pytest.mark.asyncio
async def test_browser_search_goto_timeout(page_context):
    page = AsyncMock()
    page.goto = AsyncMock(side_effect=Exception("Timeout"))
    page.query_selector = AsyncMock(return_value=None)
    page.wait_for_selector = AsyncMock()
    page.locator = MagicMock()

    async with page_context(page):
        result = await browser_search.ainvoke({"query": "test query"})

    data = json.loads(result)
    assert data["success"] is False
    assert "Timeout" in data["message"]
