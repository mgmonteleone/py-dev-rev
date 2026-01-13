"""Pagination utilities for DevRev SDK.

This module provides iterator-based pagination for list endpoints.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Iterator
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from devrev.models.base import PaginatedResponse

T = TypeVar("T")


class PaginatedIterator(Iterator[T]):
    """Iterator for synchronous paginated responses.

    Automatically fetches next pages as needed.

    Example:
        ```python
        from devrev import DevRevClient
        from devrev.utils.pagination import paginate

        client = DevRevClient()
        for account in paginate(client.accounts.list, "accounts"):
            print(account.display_name)
        ```
    """

    def __init__(
        self,
        fetch_page: Callable[[str | None], PaginatedResponse],
        items_attr: str,
        limit: int | None = None,
    ) -> None:
        """Initialize the paginated iterator.

        Args:
            fetch_page: Function that fetches a page given a cursor
            items_attr: Attribute name for items in the response
            limit: Maximum total items to return (None = unlimited)
        """
        self._fetch_page = fetch_page
        self._items_attr = items_attr
        self._limit = limit
        self._cursor: str | None = None
        self._items: list[T] = []
        self._item_index = 0
        self._total_returned = 0
        self._exhausted = False

    def __iter__(self) -> PaginatedIterator[T]:
        """Return self as iterator."""
        return self

    def __next__(self) -> T:
        """Get next item, fetching more pages as needed."""
        # Check if we've hit our limit
        if self._limit is not None and self._total_returned >= self._limit:
            raise StopIteration

        # If we've consumed all items in current page, fetch next
        while self._item_index >= len(self._items):
            if self._exhausted:
                raise StopIteration

            response = self._fetch_page(self._cursor)
            self._items = getattr(response, self._items_attr, [])
            self._item_index = 0
            self._cursor = response.next_cursor

            if not self._cursor:
                self._exhausted = True

            # If no items in this page, check if we're done
            if not self._items and self._exhausted:
                raise StopIteration

        item = self._items[self._item_index]
        self._item_index += 1
        self._total_returned += 1
        return item


class AsyncPaginatedIterator(AsyncIterator[T]):
    """Async iterator for paginated responses.

    Automatically fetches next pages as needed.

    Example:
        ```python
        from devrev import AsyncDevRevClient
        from devrev.utils.pagination import async_paginate

        async with AsyncDevRevClient() as client:
            async for account in async_paginate(client.accounts.list, "accounts"):
                print(account.display_name)
        ```
    """

    def __init__(
        self,
        fetch_page: Callable[[str | None], Any],  # Returns Awaitable
        items_attr: str,
        limit: int | None = None,
    ) -> None:
        """Initialize the async paginated iterator.

        Args:
            fetch_page: Async function that fetches a page given a cursor
            items_attr: Attribute name for items in the response
            limit: Maximum total items to return (None = unlimited)
        """
        self._fetch_page = fetch_page
        self._items_attr = items_attr
        self._limit = limit
        self._cursor: str | None = None
        self._items: list[T] = []
        self._item_index = 0
        self._total_returned = 0
        self._exhausted = False

    def __aiter__(self) -> AsyncPaginatedIterator[T]:
        """Return self as async iterator."""
        return self

    async def __anext__(self) -> T:
        """Get next item, fetching more pages as needed."""
        # Check if we've hit our limit
        if self._limit is not None and self._total_returned >= self._limit:
            raise StopAsyncIteration

        # If we've consumed all items in current page, fetch next
        while self._item_index >= len(self._items):
            if self._exhausted:
                raise StopAsyncIteration

            response = await self._fetch_page(self._cursor)
            self._items = getattr(response, self._items_attr, [])
            self._item_index = 0
            self._cursor = response.next_cursor

            if not self._cursor:
                self._exhausted = True

            if not self._items and self._exhausted:
                raise StopAsyncIteration

        item = self._items[self._item_index]
        self._item_index += 1
        self._total_returned += 1
        return item
