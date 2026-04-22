"""Conversations service for DevRev SDK."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import overload

from devrev.models.base import DateFilter
from devrev.models.conversations import (
    Conversation,
    ConversationExportItem,
    ConversationsCreateRequest,
    ConversationsCreateResponse,
    ConversationsDeleteRequest,
    ConversationsDeleteResponse,
    ConversationsExportRequest,
    ConversationsExportResponse,
    ConversationsGetRequest,
    ConversationsGetResponse,
    ConversationsListRequest,
    ConversationsListResponse,
    ConversationsUpdateRequest,
    ConversationsUpdateResponse,
)
from devrev.services._pagination import resolve_page_limit
from devrev.services.base import AsyncBaseService, BaseService


def _normalize_sort_by(sort_by: Sequence[str] | None) -> list[str] | None:
    """Normalize sort_by entries to the ``field:direction`` format.

    Accepts entries already in ``field:direction`` form (e.g.
    ``"modified_date:desc"``), the legacy ``"-field"`` shorthand for
    descending order, and bare field names (e.g. ``"modified_date"``) which
    default to ascending order.
    """
    if sort_by is None:
        return None
    normalized: list[str] = []
    for entry in sort_by:
        if ":" in entry:
            normalized.append(entry)
        elif entry.startswith("-"):
            normalized.append(f"{entry[1:]}:desc")
        else:
            normalized.append(f"{entry}:asc")
    return normalized


def _is_before_cutoff(modified_date: datetime | None, cutoff: datetime) -> bool:
    """Return True if ``modified_date`` is strictly older than ``cutoff``.

    Returns False when the timestamp is unknown or when the two datetimes have
    incompatible tz-awareness; the server-side filter remains authoritative.
    """
    if modified_date is None:
        return False
    try:
        return modified_date < cutoff
    except TypeError:
        return False


class ConversationsService(BaseService):
    """Service for managing DevRev Conversations."""

    def create(self, request: ConversationsCreateRequest) -> Conversation:
        """Create a new conversation."""
        response = self._post("/conversations.create", request, ConversationsCreateResponse)
        return response.conversation

    def get(self, request: ConversationsGetRequest) -> Conversation:
        """Get a conversation by ID."""
        response = self._post("/conversations.get", request, ConversationsGetResponse)
        return response.conversation

    def list(self, request: ConversationsListRequest | None = None) -> Sequence[Conversation]:
        """List conversations."""
        if request is None:
            request = ConversationsListRequest()
        if request.sort_by is not None:
            request.sort_by = _normalize_sort_by(request.sort_by)
        response = self._post("/conversations.list", request, ConversationsListResponse)
        return response.conversations

    def list_modified_since(
        self,
        after: datetime,
        *,
        limit: int | None = None,
        page_size: int | None = None,
    ) -> Sequence[Conversation]:
        """List conversations modified after a given datetime, newest first.

        Streams pages via cursor until the server returns no further cursor,
        ``limit`` is reached, or a conversation older than ``after`` is seen.

        Args:
            after: Only include conversations modified after this datetime.
            limit: Maximum number of conversations to return overall.
            page_size: Number of results per API request; ``None`` defers to server.

        Returns:
            List of Conversation objects modified after ``after``, newest first.
        """
        results: list[Conversation] = []
        cursor: str | None = None
        while True:
            if limit is not None and len(results) >= limit:
                break
            request_limit = resolve_page_limit(limit, len(results), page_size)
            request = ConversationsListRequest(
                cursor=cursor,
                limit=request_limit,
                modified_date=DateFilter(after=after),
                sort_by=_normalize_sort_by(["modified_date:desc"]),
            )
            response = self._post("/conversations.list", request, ConversationsListResponse)
            for conversation in response.conversations:
                if _is_before_cutoff(conversation.modified_date, after):
                    return results
                results.append(conversation)
                if limit is not None and len(results) >= limit:
                    return results
            if not response.next_cursor:
                break
            cursor = response.next_cursor
        return results

    def update(self, request: ConversationsUpdateRequest) -> Conversation:
        """Update a conversation."""
        response = self._post("/conversations.update", request, ConversationsUpdateResponse)
        return response.conversation

    def delete(self, request: ConversationsDeleteRequest) -> None:
        """Delete a conversation."""
        self._post("/conversations.delete", request, ConversationsDeleteResponse)

    @overload
    def export(
        self,
        request: ConversationsExportRequest | None = None,
    ) -> Sequence[ConversationExportItem]: ...

    @overload
    def export(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        return_response: bool = True,
    ) -> ConversationsExportResponse: ...

    def export(
        self,
        request: ConversationsExportRequest | None = None,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        return_response: bool = False,
    ) -> Sequence[ConversationExportItem] | ConversationsExportResponse:
        """Export conversations.

        This endpoint is only available with the beta API. Calling this method
        when the client is configured for the public API will result in an
        HTTP 404 error from the server.

        This method supports two calling patterns for backwards compatibility:

        1. Legacy pattern (returns just the conversations list):
           ``export()`` or ``export(request)``

        2. New pattern (returns full response with pagination):
           ``export(cursor="...", limit=10, return_response=True)``

        Args:
            request: Export request object (legacy pattern)
            cursor: Pagination cursor (new pattern)
            limit: Maximum number of results (new pattern)
            return_response: If True, return full response object (default: False for backwards compat)

        Returns:
            Sequence of ConversationExportItem objects (legacy) or ConversationsExportResponse (if return_response=True)

        Note:
            Beta API only. Use ``api_version=APIVersion.BETA`` when initializing the client.
        """
        if request is None:
            request = ConversationsExportRequest(cursor=cursor, limit=limit)
        response = self._post("/conversations.export", request, ConversationsExportResponse)
        if return_response:
            return response
        return response.conversations


class AsyncConversationsService(AsyncBaseService):
    """Async service for managing DevRev Conversations."""

    async def create(self, request: ConversationsCreateRequest) -> Conversation:
        """Create a new conversation."""
        response = await self._post("/conversations.create", request, ConversationsCreateResponse)
        return response.conversation

    async def get(self, request: ConversationsGetRequest) -> Conversation:
        """Get a conversation by ID."""
        response = await self._post("/conversations.get", request, ConversationsGetResponse)
        return response.conversation

    async def list(self, request: ConversationsListRequest | None = None) -> Sequence[Conversation]:
        """List conversations."""
        if request is None:
            request = ConversationsListRequest()
        if request.sort_by is not None:
            request.sort_by = _normalize_sort_by(request.sort_by)
        response = await self._post("/conversations.list", request, ConversationsListResponse)
        return response.conversations

    async def list_modified_since(
        self,
        after: datetime,
        *,
        limit: int | None = None,
        page_size: int | None = None,
    ) -> Sequence[Conversation]:
        """List conversations modified after a given datetime, newest first.

        Streams pages via cursor until the server returns no further cursor,
        ``limit`` is reached, or a conversation older than ``after`` is seen.

        Args:
            after: Only include conversations modified after this datetime.
            limit: Maximum number of conversations to return overall.
            page_size: Number of results per API request; ``None`` defers to server.

        Returns:
            List of Conversation objects modified after ``after``, newest first.
        """
        results: list[Conversation] = []
        cursor: str | None = None
        while True:
            if limit is not None and len(results) >= limit:
                break
            request_limit = resolve_page_limit(limit, len(results), page_size)
            request = ConversationsListRequest(
                cursor=cursor,
                limit=request_limit,
                modified_date=DateFilter(after=after),
                sort_by=_normalize_sort_by(["modified_date:desc"]),
            )
            response = await self._post("/conversations.list", request, ConversationsListResponse)
            for conversation in response.conversations:
                if _is_before_cutoff(conversation.modified_date, after):
                    return results
                results.append(conversation)
                if limit is not None and len(results) >= limit:
                    return results
            if not response.next_cursor:
                break
            cursor = response.next_cursor
        return results

    async def update(self, request: ConversationsUpdateRequest) -> Conversation:
        """Update a conversation."""
        response = await self._post("/conversations.update", request, ConversationsUpdateResponse)
        return response.conversation

    async def delete(self, request: ConversationsDeleteRequest) -> None:
        """Delete a conversation."""
        await self._post("/conversations.delete", request, ConversationsDeleteResponse)

    @overload
    async def export(
        self,
        request: ConversationsExportRequest | None = None,
    ) -> Sequence[ConversationExportItem]: ...

    @overload
    async def export(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        return_response: bool = True,
    ) -> ConversationsExportResponse: ...

    async def export(
        self,
        request: ConversationsExportRequest | None = None,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        return_response: bool = False,
    ) -> Sequence[ConversationExportItem] | ConversationsExportResponse:
        """Export conversations.

        This endpoint is only available with the beta API. Calling this method
        when the client is configured for the public API will result in an
        HTTP 404 error from the server.

        This method supports two calling patterns for backwards compatibility:

        1. Legacy pattern (returns just the conversations list):
           ``await export()`` or ``await export(request)``

        2. New pattern (returns full response with pagination):
           ``await export(cursor="...", limit=10, return_response=True)``

        Args:
            request: Export request object (legacy pattern)
            cursor: Pagination cursor (new pattern)
            limit: Maximum number of results (new pattern)
            return_response: If True, return full response object (default: False for backwards compat)

        Returns:
            Sequence of ConversationExportItem objects (legacy) or ConversationsExportResponse (if return_response=True)

        Note:
            Beta API only. Use ``api_version=APIVersion.BETA`` when initializing the client.
        """
        if request is None:
            request = ConversationsExportRequest(cursor=cursor, limit=limit)
        response = await self._post("/conversations.export", request, ConversationsExportResponse)
        if return_response:
            return response
        return response.conversations
