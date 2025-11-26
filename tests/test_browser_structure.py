"""Tests for browser_get_structure tool."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from hallw.tools.playwright import structure


@pytest.mark.asyncio
async def test_browser_get_structure_filters_visible(monkeypatch):
    page = AsyncMock()
    page.accessibility.snapshot = AsyncMock(
        return_value={
            "role": "document",
            "children": [
                {"role": "button", "name": "Submit"},
                {"role": "link", "name": "Home"},
                {"role": "textbox", "name": ""},  # ignored empty name
            ],
        }
    )
    locator = _build_locator(count=1, is_visible=True)
    page.get_by_role = MagicMock(return_value=locator)
    page.title = AsyncMock(return_value="My Page")
    page.url = "https://example.com"

    monkeypatch.setattr(structure, "get_page", AsyncMock(return_value=page))

    data = json.loads(await structure.browser_get_structure.ainvoke({"page_index": 0}))

    assert data["success"] is True
    roles = [item["role"] for item in data["data"]["interactive_elements"]]
    assert roles == ["button", "link"]


def _build_locator(count=1, is_visible=True):
    locator = AsyncMock()
    locator.count = AsyncMock(return_value=count)
    locator.nth = MagicMock(return_value=locator)
    locator.is_visible = AsyncMock(return_value=is_visible)
    return locator
