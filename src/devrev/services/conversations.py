"""Conversations service for DevRev SDK."""

from __future__ import annotations

from collections.abc import Sequence
from typing import overload

from devrev.models.conversations import (
    Conversation,
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
from devrev.services.base import AsyncBaseService, BaseService


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
        response = self._post("/conversations.list", request, ConversationsListResponse)
        return response.conversations

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
    ) -> Sequence[Conversation]: ...

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
    ) -> Sequence[Conversation] | ConversationsExportResponse:
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
            Sequence of Conversation objects (legacy) or ConversationsExportResponse (if return_response=True)

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
        response = await self._post("/conversations.list", request, ConversationsListResponse)
        return response.conversations

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
    ) -> Sequence[Conversation]: ...

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
    ) -> Sequence[Conversation] | ConversationsExportResponse:
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
            Sequence of Conversation objects (legacy) or ConversationsExportResponse (if return_response=True)

        Note:
            Beta API only. Use ``api_version=APIVersion.BETA`` when initializing the client.
        """
        if request is None:
            request = ConversationsExportRequest(cursor=cursor, limit=limit)
        response = await self._post("/conversations.export", request, ConversationsExportResponse)
        if return_response:
            return response
        return response.conversations
