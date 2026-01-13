"""Webhooks service for DevRev SDK."""

from __future__ import annotations

from collections.abc import Sequence

from devrev.models.webhooks import (
    Webhook,
    WebhooksCreateRequest,
    WebhooksCreateResponse,
    WebhooksDeleteRequest,
    WebhooksDeleteResponse,
    WebhooksGetRequest,
    WebhooksGetResponse,
    WebhooksListRequest,
    WebhooksListResponse,
    WebhooksUpdateRequest,
    WebhooksUpdateResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


class WebhooksService(BaseService):
    """Service for managing DevRev Webhooks."""

    def create(self, request: WebhooksCreateRequest) -> Webhook:
        """Create a new webhook."""
        response = self._post("/webhooks.create", request, WebhooksCreateResponse)
        return response.webhook

    def get(self, request: WebhooksGetRequest) -> Webhook:
        """Get a webhook by ID."""
        response = self._post("/webhooks.get", request, WebhooksGetResponse)
        return response.webhook

    def list(self, request: WebhooksListRequest | None = None) -> Sequence[Webhook]:
        """List webhooks."""
        if request is None:
            request = WebhooksListRequest()
        response = self._post("/webhooks.list", request, WebhooksListResponse)
        return response.webhooks

    def update(self, request: WebhooksUpdateRequest) -> Webhook:
        """Update a webhook."""
        response = self._post("/webhooks.update", request, WebhooksUpdateResponse)
        return response.webhook

    def delete(self, request: WebhooksDeleteRequest) -> None:
        """Delete a webhook."""
        self._post("/webhooks.delete", request, WebhooksDeleteResponse)


class AsyncWebhooksService(AsyncBaseService):
    """Async service for managing DevRev Webhooks."""

    async def create(self, request: WebhooksCreateRequest) -> Webhook:
        """Create a new webhook."""
        response = await self._post(
            "/webhooks.create", request, WebhooksCreateResponse
        )
        return response.webhook

    async def get(self, request: WebhooksGetRequest) -> Webhook:
        """Get a webhook by ID."""
        response = await self._post("/webhooks.get", request, WebhooksGetResponse)
        return response.webhook

    async def list(
        self, request: WebhooksListRequest | None = None
    ) -> Sequence[Webhook]:
        """List webhooks."""
        if request is None:
            request = WebhooksListRequest()
        response = await self._post("/webhooks.list", request, WebhooksListResponse)
        return response.webhooks

    async def update(self, request: WebhooksUpdateRequest) -> Webhook:
        """Update a webhook."""
        response = await self._post(
            "/webhooks.update", request, WebhooksUpdateResponse
        )
        return response.webhook

    async def delete(self, request: WebhooksDeleteRequest) -> None:
        """Delete a webhook."""
        await self._post("/webhooks.delete", request, WebhooksDeleteResponse)

