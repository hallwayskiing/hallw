"""Tests for browser_open_new_page tool."""

import json
from unittest.mock import AsyncMock

import pytest

from hallw.tools.playwright import new_page


@pytest.mark.asyncio
async def test_browser_open_new_page_success(monkeypatch):
    monkeypatch.setattr(new_page, "add_page", AsyncMock(return_value=2))

    data = json.loads(await new_page.browser_open_new_page.ainvoke({}))

    assert data["success"] is True
    assert data["data"]["page_index"] == 2


@pytest.mark.asyncio
async def test_browser_open_new_page_failure(monkeypatch):
    monkeypatch.setattr(new_page, "add_page", AsyncMock(side_effect=Exception("boom")))

    data = json.loads(await new_page.browser_open_new_page.ainvoke({}))

    assert data["success"] is False
    assert "Failed" in data["message"]
