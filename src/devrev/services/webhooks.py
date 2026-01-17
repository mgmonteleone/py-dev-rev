"""Webhooks service for DevRev SDK."""

from __future__ import annotations

from collections.abc import Sequence

from devrev.models.webhooks import (
    Webhook,
    WebhooksCreateRequest,
    WebhooksCreateResponse,
    WebhooksDeleteRequest,
    WebhooksDeleteResponse,
    WebhooksFetchRequest,
    WebhooksFetchResponse,
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

    def fetch(
        self,
        id: str,
    ) -> dict[str, object]:
        """Fetch webhook data (beta only).

        Args:
            id: Webhook ID

        Returns:
            Webhook data dictionary

        Raises:
            BetaAPIRequiredError: If not using beta API
        """
        request = WebhooksFetchRequest(id=id)
        response = self._post("/webhooks.fetch", request, WebhooksFetchResponse)
        return response.data


class AsyncWebhooksService(AsyncBaseService):
    """Async service for managing DevRev Webhooks."""

    async def create(self, request: WebhooksCreateRequest) -> Webhook:
        """Create a new webhook."""
        response = await self._post("/webhooks.create", request, WebhooksCreateResponse)
        return response.webhook

    async def get(self, request: WebhooksGetRequest) -> Webhook:
        """Get a webhook by ID."""
        response = await self._post("/webhooks.get", request, WebhooksGetResponse)
        return response.webhook

    async def list(self, request: WebhooksListRequest | None = None) -> Sequence[Webhook]:
        """List webhooks."""
        if request is None:
            request = WebhooksListRequest()
        response = await self._post("/webhooks.list", request, WebhooksListResponse)
        return response.webhooks

    async def update(self, request: WebhooksUpdateRequest) -> Webhook:
        """Update a webhook."""
        response = await self._post("/webhooks.update", request, WebhooksUpdateResponse)
        return response.webhook

    async def delete(self, request: WebhooksDeleteRequest) -> None:
        """Delete a webhook."""
        await self._post("/webhooks.delete", request, WebhooksDeleteResponse)

    async def fetch(
        self,
        id: str,
    ) -> dict[str, object]:
        """Fetch webhook data (beta only).

        Args:
            id: Webhook ID

        Returns:
            Webhook data dictionary

        Raises:
            BetaAPIRequiredError: If not using beta API
        """
        request = WebhooksFetchRequest(id=id)
        response = await self._post("/webhooks.fetch", request, WebhooksFetchResponse)
        return response.data
