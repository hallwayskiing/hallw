"""Tests for the browser_get_structure tool."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from hallw.tools.playwright.structure import browser_get_structure


@pytest.mark.asyncio
async def test_browser_get_structure_success(page_context):
    page = AsyncMock()
    page.title = AsyncMock(return_value="Test Page Title")
    page.url = "https://example.com"
    page.accessibility = AsyncMock()

    snapshot = {
        "role": "WebArea",
        "name": "",
        "children": [
            {"role": "button", "name": "Submit Button", "children": []},
            {"role": "link", "name": "Home", "children": []},
            {"role": "textbox", "name": "Search", "children": []},
        ],
    }
    page.accessibility.snapshot = AsyncMock(return_value=snapshot)

    locator = AsyncMock()
    locator.count = AsyncMock(return_value=1)
    locator.nth = MagicMock(return_value=locator)
    locator.is_visible = AsyncMock(return_value=True)
    page.get_by_role = MagicMock(return_value=locator)

    async with page_context(page):
        result = await browser_get_structure.ainvoke({})

    data = json.loads(result)
    assert data["success"] is True
    assert data["data"]["title"] == "Test Page Title"
    assert len(data["data"]["interactive_elements"]) == 3


@pytest.mark.asyncio
async def test_browser_get_structure_filters_invisible(page_context):
    page = AsyncMock()
    page.title = AsyncMock(return_value="Test Page")
    page.url = "https://example.com"
    page.accessibility = AsyncMock()

    snapshot = {
        "role": "WebArea",
        "name": "",
        "children": [
            {"role": "button", "name": "Visible Button", "children": []},
            {"role": "button", "name": "Hidden Button", "children": []},
        ],
    }
    page.accessibility.snapshot = AsyncMock(return_value=snapshot)

    visible_locator = AsyncMock()
    visible_locator.count = AsyncMock(return_value=1)
    visible_locator.nth = MagicMock(return_value=visible_locator)
    visible_locator.is_visible = AsyncMock(return_value=True)

    hidden_locator = AsyncMock()
    hidden_locator.count = AsyncMock(return_value=1)
    hidden_locator.nth = MagicMock(return_value=hidden_locator)
    hidden_locator.is_visible = AsyncMock(return_value=False)

    def locator_side_effect(role, name, exact=None):
        return visible_locator if name == "Visible Button" else hidden_locator

    page.get_by_role = MagicMock(side_effect=locator_side_effect)

    async with page_context(page):
        result = await browser_get_structure.ainvoke({})

    data = json.loads(result)
    element_names = [elem["name"] for elem in data["data"]["interactive_elements"]]
    assert element_names == ["Visible Button"]


@pytest.mark.asyncio
async def test_browser_get_structure_filters_allowed_roles(page_context):
    page = AsyncMock()
    page.title = AsyncMock(return_value="Test Page")
    page.url = "https://example.com"
    page.accessibility = AsyncMock()

    snapshot = {
        "role": "WebArea",
        "name": "",
        "children": [
            {"role": "button", "name": "Button", "children": []},
            {"role": "heading", "name": "Heading", "children": []},
            {"role": "link", "name": "Link", "children": []},
        ],
    }
    page.accessibility.snapshot = AsyncMock(return_value=snapshot)

    locator = AsyncMock()
    locator.count = AsyncMock(return_value=1)
    locator.nth = MagicMock(return_value=locator)
    locator.is_visible = AsyncMock(return_value=True)
    page.get_by_role = MagicMock(return_value=locator)

    async with page_context(page):
        result = await browser_get_structure.ainvoke({})

    data = json.loads(result)
    roles = [elem["role"] for elem in data["data"]["interactive_elements"]]
    assert "button" in roles
    assert "link" in roles
    assert "heading" not in roles


@pytest.mark.asyncio
async def test_browser_get_structure_handles_timeout(page_context):
    page = AsyncMock()
    page.title = AsyncMock(return_value="Test Page")
    page.url = "https://example.com"
    page.accessibility = AsyncMock()

    snapshot = {
        "role": "WebArea",
        "name": "",
        "children": [{"role": "button", "name": "Test Button", "children": []}],
    }
    page.accessibility.snapshot = AsyncMock(return_value=snapshot)

    locator = AsyncMock()
    locator.count = AsyncMock(side_effect=PlaywrightTimeoutError("Timeout"))
    page.get_by_role = MagicMock(return_value=locator)

    async with page_context(page):
        result = await browser_get_structure.ainvoke({})

    data = json.loads(result)
    assert data["success"] is True
    assert data["data"]["interactive_elements"] == []
