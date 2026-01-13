"""Conversations service for DevRev SDK."""

from __future__ import annotations

from collections.abc import Sequence

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
        response = self._post(
            "/conversations.create", request, ConversationsCreateResponse
        )
        return response.conversation

    def get(self, request: ConversationsGetRequest) -> Conversation:
        """Get a conversation by ID."""
        response = self._post(
            "/conversations.get", request, ConversationsGetResponse
        )
        return response.conversation

    def list(
        self, request: ConversationsListRequest | None = None
    ) -> Sequence[Conversation]:
        """List conversations."""
        if request is None:
            request = ConversationsListRequest()
        response = self._post(
            "/conversations.list", request, ConversationsListResponse
        )
        return response.conversations

    def update(self, request: ConversationsUpdateRequest) -> Conversation:
        """Update a conversation."""
        response = self._post(
            "/conversations.update", request, ConversationsUpdateResponse
        )
        return response.conversation

    def delete(self, request: ConversationsDeleteRequest) -> None:
        """Delete a conversation."""
        self._post("/conversations.delete", request, ConversationsDeleteResponse)

    def export(
        self, request: ConversationsExportRequest | None = None
    ) -> Sequence[Conversation]:
        """Export conversations."""
        if request is None:
            request = ConversationsExportRequest()
        response = self._post(
            "/conversations.export", request, ConversationsExportResponse
        )
        return response.conversations


class AsyncConversationsService(AsyncBaseService):
    """Async service for managing DevRev Conversations."""

    async def create(self, request: ConversationsCreateRequest) -> Conversation:
        """Create a new conversation."""
        response = await self._post(
            "/conversations.create", request, ConversationsCreateResponse
        )
        return response.conversation

    async def get(self, request: ConversationsGetRequest) -> Conversation:
        """Get a conversation by ID."""
        response = await self._post(
            "/conversations.get", request, ConversationsGetResponse
        )
        return response.conversation

    async def list(
        self, request: ConversationsListRequest | None = None
    ) -> Sequence[Conversation]:
        """List conversations."""
        if request is None:
            request = ConversationsListRequest()
        response = await self._post(
            "/conversations.list", request, ConversationsListResponse
        )
        return response.conversations

    async def update(self, request: ConversationsUpdateRequest) -> Conversation:
        """Update a conversation."""
        response = await self._post(
            "/conversations.update", request, ConversationsUpdateResponse
        )
        return response.conversation

    async def delete(self, request: ConversationsDeleteRequest) -> None:
        """Delete a conversation."""
        await self._post(
            "/conversations.delete", request, ConversationsDeleteResponse
        )

    async def export(
        self, request: ConversationsExportRequest | None = None
    ) -> Sequence[Conversation]:
        """Export conversations."""
        if request is None:
            request = ConversationsExportRequest()
        response = await self._post(
            "/conversations.export", request, ConversationsExportResponse
        )
        return response.conversations

