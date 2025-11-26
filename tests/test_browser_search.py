"""Coverage tests for browser_search tool."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from hallw.tools.playwright import search
from hallw.utils import Events


@pytest.mark.asyncio
async def test_browser_search_success(monkeypatch):
    page = _build_page_with_results(["Title 1", "Title 2"], ["https://a.com", "https://b.com"])

    monkeypatch.setattr(search, "get_page", AsyncMock(return_value=page))
    monkeypatch.setattr(search, "emit", lambda *_args, **_kwargs: None)

    data = json.loads(await search.browser_search.ainvoke({"page_index": 0, "query": "q"}))

    assert data["success"] is True
    assert len(data["data"]["results"]) == 2
    page.goto.assert_awaited()
    page.wait_for_selector.assert_awaited()


@pytest.mark.asyncio
async def test_browser_search_captcha_flow(monkeypatch):
    # First captcha selector hits, rest are skipped by break
    page = _build_page_with_results(["One"], ["https://one.com"])
    page.query_selector = AsyncMock(side_effect=[True])

    emitted = []

    def fake_emit(event, payload):
        emitted.append((event, payload))

    monkeypatch.setattr(search, "get_page", AsyncMock(return_value=page))
    monkeypatch.setattr(search, "emit", fake_emit)

    data = json.loads(await search.browser_search.ainvoke({"page_index": 1, "query": "hi"}))

    assert data["success"] is True
    assert any(e[0] == Events.CAPTCHA_DETECTED for e in emitted)
    assert any(e[0] == Events.CAPTCHA_RESOLVED for e in emitted)


@pytest.mark.asyncio
async def test_browser_search_returns_error_when_page_missing(monkeypatch):
    monkeypatch.setattr(search, "get_page", AsyncMock(return_value=None))

    data = json.loads(await search.browser_search.ainvoke({"page_index": 3, "query": "q"}))

    assert data["success"] is False
    assert "not found" in data["message"]


@pytest.mark.asyncio
async def test_browser_search_handles_navigation_error(monkeypatch):
    page = _build_page_with_results(["One"], ["https://one.com"])
    page.goto = AsyncMock(side_effect=Exception("Timeout"))

    monkeypatch.setattr(search, "get_page", AsyncMock(return_value=page))
    monkeypatch.setattr(search, "emit", lambda *_args, **_kwargs: None)

    data = json.loads(await search.browser_search.ainvoke({"page_index": 0, "query": "q"}))

    assert data["success"] is False
    assert "Timeout" in data["message"]


@pytest.mark.asyncio
async def test_browser_search_no_results(monkeypatch):
    page = AsyncMock()
    page.goto = AsyncMock()
    page.query_selector = AsyncMock(return_value=None)
    page.wait_for_selector = AsyncMock()
    link_locators = AsyncMock()
    link_locators.count = AsyncMock(return_value=0)
    page.locator = MagicMock(return_value=link_locators)

    monkeypatch.setattr(search, "get_page", AsyncMock(return_value=page))
    monkeypatch.setattr(search, "emit", lambda *_args, **_kwargs: None)

    data = json.loads(await search.browser_search.ainvoke({"page_index": 0, "query": "q"}))

    assert data["success"] is False
    assert "No valid search results" in data["message"]


def _build_page_with_results(titles, urls):
    page = AsyncMock()
    page.goto = AsyncMock()
    page.query_selector = AsyncMock(return_value=None)
    page.wait_for_selector = AsyncMock()

    link_locators = AsyncMock()
    link_locators.count = AsyncMock(return_value=len(titles))

    entries = []
    for title, url in zip(titles, urls):
        child = AsyncMock()
        child.count = AsyncMock(return_value=1)
        child.inner_text = AsyncMock(return_value=title)

        entry = AsyncMock()
        entry.get_attribute = AsyncMock(return_value=url)
        entry.locator = MagicMock(return_value=child)
        entry.inner_text = AsyncMock(return_value=title)
        entries.append(entry)

    link_locators.nth = MagicMock(side_effect=entries)
    page.locator = MagicMock(return_value=link_locators)

    return page
