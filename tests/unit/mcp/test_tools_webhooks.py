"""Unit tests for DevRev MCP webhook tools."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from devrev.exceptions import NotFoundError, ValidationError
from devrev_mcp.tools.webhooks import (
    devrev_webhooks_create,
    devrev_webhooks_delete,
    devrev_webhooks_get,
    devrev_webhooks_list,
    devrev_webhooks_update,
)

WEBHOOK_ID = "don:integration:dvrv-us-1:devo/1:webhook/123"


def _make_mock_webhook(data: dict | None = None) -> MagicMock:
    """Create a mock Webhook model with a model_dump method."""
    mock = MagicMock()
    default_data = {
        "id": WEBHOOK_ID,
        "url": "https://example.com/hook",
        "status": "active",
        "event_types": ["work_created"],
        "created_date": "2026-01-01T00:00:00Z",
        "modified_date": "2026-01-01T00:00:00Z",
    }
    if data:
        default_data.update(data)
    mock.model_dump.return_value = default_data
    return mock


class TestWebhooksListTool:
    """Tests for devrev_webhooks_list tool."""

    async def test_webhooks_list_success(self, mock_ctx, mock_client):
        """Test listing webhooks with results."""
        webhook = _make_mock_webhook()
        mock_client.webhooks.list.return_value = [webhook]

        result = await devrev_webhooks_list(mock_ctx)

        assert result["count"] == 1
        assert len(result["webhooks"]) == 1
        assert result["webhooks"][0]["id"] == WEBHOOK_ID
        assert result["webhooks"][0]["url"] == "https://example.com/hook"
        mock_client.webhooks.list.assert_called_once()

    async def test_webhooks_list_empty(self, mock_ctx, mock_client):
        """Test listing webhooks with empty results."""
        mock_client.webhooks.list.return_value = []

        result = await devrev_webhooks_list(mock_ctx)

        assert result["count"] == 0
        assert result["webhooks"] == []
        mock_client.webhooks.list.assert_called_once()

    async def test_webhooks_list_with_pagination(self, mock_ctx, mock_client):
        """Test listing webhooks with pagination parameters."""
        wh1 = _make_mock_webhook({"id": "wh-1"})
        wh2 = _make_mock_webhook({"id": "wh-2"})
        mock_client.webhooks.list.return_value = [wh1, wh2]

        result = await devrev_webhooks_list(mock_ctx, cursor="cursor-123", limit=10)

        assert result["count"] == 2
        assert len(result["webhooks"]) == 2
        mock_client.webhooks.list.assert_called_once()

    async def test_webhooks_list_error(self, mock_ctx, mock_client):
        """Test listing webhooks with error."""
        mock_client.webhooks.list.side_effect = NotFoundError("Not found", status_code=404)

        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_webhooks_list(mock_ctx)


class TestWebhooksGetTool:
    """Tests for devrev_webhooks_get tool."""

    async def test_webhooks_get_success(self, mock_ctx, mock_client):
        """Test getting a webhook successfully."""
        mock_client.webhooks.get.return_value = _make_mock_webhook()

        result = await devrev_webhooks_get(mock_ctx, id=WEBHOOK_ID)

        assert result["id"] == WEBHOOK_ID
        assert result["url"] == "https://example.com/hook"
        mock_client.webhooks.get.assert_called_once()

    async def test_webhooks_get_error(self, mock_ctx, mock_client):
        """Test getting a non-existent webhook."""
        mock_client.webhooks.get.side_effect = NotFoundError("Webhook not found", status_code=404)

        with pytest.raises(RuntimeError, match="Webhook not found"):
            await devrev_webhooks_get(mock_ctx, id=WEBHOOK_ID)

    async def test_webhooks_get_wrong_id_type(self, mock_ctx, mock_client):
        """Test getting a webhook with a non-webhook DON ID raises."""
        with pytest.raises(RuntimeError, match="expects"):
            await devrev_webhooks_get(mock_ctx, id="don:core:dvrv-us-1:devo/1:account/1")
        mock_client.webhooks.get.assert_not_called()


class TestWebhooksCreateTool:
    """Tests for devrev_webhooks_create tool."""

    async def test_webhooks_create_minimal(self, mock_ctx, mock_client):
        """Test creating a webhook with minimal parameters."""
        mock_client.webhooks.create.return_value = _make_mock_webhook()

        result = await devrev_webhooks_create(mock_ctx, url="https://example.com/hook")

        assert result["url"] == "https://example.com/hook"
        mock_client.webhooks.create.assert_called_once()

    async def test_webhooks_create_full(self, mock_ctx, mock_client):
        """Test creating a webhook with all parameters."""
        mock_client.webhooks.create.return_value = _make_mock_webhook(
            {"event_types": ["work_created", "work_updated"]}
        )

        result = await devrev_webhooks_create(
            mock_ctx,
            url="https://example.com/hook",
            event_types=["work_created", "work_updated"],
            secret="s3cr3t",
        )

        assert result["event_types"] == ["work_created", "work_updated"]
        mock_client.webhooks.create.assert_called_once()

    async def test_webhooks_create_validation_error(self, mock_ctx, mock_client):
        """Test creating a webhook with validation error."""
        mock_client.webhooks.create.side_effect = ValidationError("Invalid url", status_code=400)

        with pytest.raises(RuntimeError, match="Invalid url"):
            await devrev_webhooks_create(mock_ctx, url="not-a-url")


class TestWebhooksUpdateTool:
    """Tests for devrev_webhooks_update tool."""

    async def test_webhooks_update_success(self, mock_ctx, mock_client):
        """Test updating a webhook successfully."""
        mock_client.webhooks.update.return_value = _make_mock_webhook(
            {"url": "https://new.example.com/hook"}
        )

        result = await devrev_webhooks_update(
            mock_ctx, id=WEBHOOK_ID, url="https://new.example.com/hook"
        )

        assert result["url"] == "https://new.example.com/hook"
        mock_client.webhooks.update.assert_called_once()

    async def test_webhooks_update_status(self, mock_ctx, mock_client):
        """Test updating a webhook status."""
        mock_client.webhooks.update.return_value = _make_mock_webhook({"status": "inactive"})

        result = await devrev_webhooks_update(mock_ctx, id=WEBHOOK_ID, status="inactive")

        assert result["status"] == "inactive"
        mock_client.webhooks.update.assert_called_once()

    async def test_webhooks_update_invalid_status(self, mock_ctx, mock_client):
        """Test updating a webhook with an invalid status raises."""
        with pytest.raises(RuntimeError, match="Invalid webhook status"):
            await devrev_webhooks_update(mock_ctx, id=WEBHOOK_ID, status="bogus")
        mock_client.webhooks.update.assert_not_called()

    async def test_webhooks_update_error(self, mock_ctx, mock_client):
        """Test updating a webhook with error."""
        mock_client.webhooks.update.side_effect = NotFoundError(
            "Webhook not found", status_code=404
        )

        with pytest.raises(RuntimeError, match="Webhook not found"):
            await devrev_webhooks_update(mock_ctx, id=WEBHOOK_ID, url="https://x.example.com")


class TestWebhooksDeleteTool:
    """Tests for devrev_webhooks_delete tool."""

    async def test_webhooks_delete_success(self, mock_ctx, mock_client):
        """Test deleting a webhook successfully."""
        mock_client.webhooks.delete.return_value = None

        result = await devrev_webhooks_delete(mock_ctx, id=WEBHOOK_ID)

        assert result == {"deleted": True, "id": WEBHOOK_ID}
        mock_client.webhooks.delete.assert_called_once()

    async def test_webhooks_delete_error(self, mock_ctx, mock_client):
        """Test deleting a webhook with error."""
        mock_client.webhooks.delete.side_effect = NotFoundError(
            "Webhook not found", status_code=404
        )

        with pytest.raises(RuntimeError, match="Webhook not found"):
            await devrev_webhooks_delete(mock_ctx, id=WEBHOOK_ID)
