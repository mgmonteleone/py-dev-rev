"""Unit tests for WebhooksService."""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.webhooks import (
    Webhook,
    WebhooksCreateRequest,
    WebhooksDeleteRequest,
    WebhooksGetRequest,
    WebhooksListRequest,
    WebhooksUpdateRequest,
)
from devrev.services.webhooks import WebhooksService

from .conftest import create_mock_response


class TestWebhooksService:
    """Tests for WebhooksService."""

    def test_create_webhook(
        self,
        mock_http_client: MagicMock,
        sample_webhook_data: dict[str, Any],
    ) -> None:
        """Test creating a webhook."""
        mock_http_client.post.return_value = create_mock_response(
            {"webhook": sample_webhook_data}
        )

        service = WebhooksService(mock_http_client)
        request = WebhooksCreateRequest(
            url="https://example.com/webhook",
            event_types=["work.created", "work.updated"],
        )
        result = service.create(request)

        assert isinstance(result, Webhook)
        assert result.id == "don:core:webhook:123"
        assert result.url == "https://example.com/webhook"
        mock_http_client.post.assert_called_once()

    def test_get_webhook(
        self,
        mock_http_client: MagicMock,
        sample_webhook_data: dict[str, Any],
    ) -> None:
        """Test getting a webhook by ID."""
        mock_http_client.post.return_value = create_mock_response(
            {"webhook": sample_webhook_data}
        )

        service = WebhooksService(mock_http_client)
        request = WebhooksGetRequest(id="don:core:webhook:123")
        result = service.get(request)

        assert isinstance(result, Webhook)
        assert result.id == "don:core:webhook:123"
        mock_http_client.post.assert_called_once()

    def test_list_webhooks(
        self,
        mock_http_client: MagicMock,
        sample_webhook_data: dict[str, Any],
    ) -> None:
        """Test listing webhooks."""
        mock_http_client.post.return_value = create_mock_response(
            {"webhooks": [sample_webhook_data]}
        )

        service = WebhooksService(mock_http_client)
        result = service.list()

        assert len(result) == 1
        assert isinstance(result[0], Webhook)
        assert result[0].id == "don:core:webhook:123"
        mock_http_client.post.assert_called_once()

    def test_list_webhooks_with_request(
        self,
        mock_http_client: MagicMock,
        sample_webhook_data: dict[str, Any],
    ) -> None:
        """Test listing webhooks with pagination."""
        mock_http_client.post.return_value = create_mock_response(
            {"webhooks": [sample_webhook_data]}
        )

        service = WebhooksService(mock_http_client)
        request = WebhooksListRequest(limit=50, cursor="next-cursor")
        result = service.list(request)

        assert len(result) == 1
        mock_http_client.post.assert_called_once()

    def test_update_webhook(
        self,
        mock_http_client: MagicMock,
        sample_webhook_data: dict[str, Any],
    ) -> None:
        """Test updating a webhook."""
        updated_data = {**sample_webhook_data, "url": "https://new.example.com/webhook"}
        mock_http_client.post.return_value = create_mock_response(
            {"webhook": updated_data}
        )

        service = WebhooksService(mock_http_client)
        request = WebhooksUpdateRequest(
            id="don:core:webhook:123",
            url="https://new.example.com/webhook",
        )
        result = service.update(request)

        assert isinstance(result, Webhook)
        assert result.url == "https://new.example.com/webhook"
        mock_http_client.post.assert_called_once()

    def test_delete_webhook(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test deleting a webhook."""
        mock_http_client.post.return_value = create_mock_response({})

        service = WebhooksService(mock_http_client)
        request = WebhooksDeleteRequest(id="don:core:webhook:123")
        result = service.delete(request)

        assert result is None
        mock_http_client.post.assert_called_once()

    def test_list_webhooks_empty(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test listing webhooks returns empty list."""
        mock_http_client.post.return_value = create_mock_response(
            {"webhooks": []}
        )

        service = WebhooksService(mock_http_client)
        result = service.list()

        assert len(result) == 0
        mock_http_client.post.assert_called_once()

