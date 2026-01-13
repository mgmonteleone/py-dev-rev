"""Unit tests for pagination utilities."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from devrev.utils.pagination import AsyncPaginatedIterator, PaginatedIterator


class MockPaginatedResponse:
    """Mock paginated response for testing."""

    def __init__(self, items: list[Any], next_cursor: str | None = None) -> None:
        self.items = items
        self.next_cursor = next_cursor


class TestPaginatedIterator:
    """Tests for PaginatedIterator class."""

    def test_single_page_iteration(self) -> None:
        items = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        fetch_page = MagicMock(return_value=MockPaginatedResponse(items, None))
        iterator = PaginatedIterator(fetch_page, "items")
        result = list(iterator)
        assert result == items
        fetch_page.assert_called_once_with(None)

    def test_multi_page_iteration(self) -> None:
        page1_items = [{"id": "1"}, {"id": "2"}]
        page2_items = [{"id": "3"}, {"id": "4"}]
        page3_items = [{"id": "5"}]
        responses = [
            MockPaginatedResponse(page1_items, "cursor1"),
            MockPaginatedResponse(page2_items, "cursor2"),
            MockPaginatedResponse(page3_items, None),
        ]
        fetch_page = MagicMock(side_effect=responses)
        iterator = PaginatedIterator(fetch_page, "items")
        result = list(iterator)
        assert result == page1_items + page2_items + page3_items
        assert fetch_page.call_count == 3

    def test_empty_response(self) -> None:
        fetch_page = MagicMock(return_value=MockPaginatedResponse([], None))
        iterator = PaginatedIterator(fetch_page, "items")
        result = list(iterator)
        assert result == []

    def test_limit_parameter(self) -> None:
        items = [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"}, {"id": "5"}]
        fetch_page = MagicMock(return_value=MockPaginatedResponse(items, "cursor"))
        iterator = PaginatedIterator(fetch_page, "items", limit=3)
        result = list(iterator)
        assert len(result) == 3
        assert result == items[:3]

    def test_iter_returns_self(self) -> None:
        fetch_page = MagicMock(return_value=MockPaginatedResponse([], None))
        iterator = PaginatedIterator(fetch_page, "items")
        assert iter(iterator) is iterator


class TestAsyncPaginatedIterator:
    """Tests for AsyncPaginatedIterator class."""

    @pytest.mark.asyncio
    async def test_single_page_iteration(self) -> None:
        items = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        fetch_page = AsyncMock(return_value=MockPaginatedResponse(items, None))
        iterator = AsyncPaginatedIterator(fetch_page, "items")
        result = [item async for item in iterator]
        assert result == items

    @pytest.mark.asyncio
    async def test_multi_page_iteration(self) -> None:
        page1_items = [{"id": "1"}, {"id": "2"}]
        page2_items = [{"id": "3"}]
        responses = [
            MockPaginatedResponse(page1_items, "cursor1"),
            MockPaginatedResponse(page2_items, None),
        ]
        fetch_page = AsyncMock(side_effect=responses)
        iterator = AsyncPaginatedIterator(fetch_page, "items")
        result = [item async for item in iterator]
        assert result == page1_items + page2_items

    @pytest.mark.asyncio
    async def test_empty_response(self) -> None:
        fetch_page = AsyncMock(return_value=MockPaginatedResponse([], None))
        iterator = AsyncPaginatedIterator(fetch_page, "items")
        result = [item async for item in iterator]
        assert result == []

    @pytest.mark.asyncio
    async def test_limit_parameter(self) -> None:
        items = [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"}]
        fetch_page = AsyncMock(return_value=MockPaginatedResponse(items, "cursor"))
        iterator = AsyncPaginatedIterator(fetch_page, "items", limit=2)
        result = [item async for item in iterator]
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_aiter_returns_self(self) -> None:
        fetch_page = AsyncMock(return_value=MockPaginatedResponse([], None))
        iterator = AsyncPaginatedIterator(fetch_page, "items")
        assert iterator.__aiter__() is iterator

