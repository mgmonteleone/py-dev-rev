"""Unit tests for NotificationsService.

Refs #92
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from devrev.models.notifications import NotificationsSendResponse
from devrev.services.notifications import AsyncNotificationsService, NotificationsService

from .conftest import create_mock_response


class TestNotificationsService:
    """Tests for NotificationsService."""

    def test_send_notification_minimal(
        self,
        mock_http_client: MagicMock,
        sample_notification_send_response_data: dict[str, Any],
    ) -> None:
        """Test sending a notification with minimal parameters."""
        mock_http_client.post.return_value = create_mock_response(
            sample_notification_send_response_data
        )

        service = NotificationsService(mock_http_client)
        result = service.send(
            recipient_id="don:identity:user:456",
            message="Your ticket has been updated",
        )

        assert isinstance(result, NotificationsSendResponse)
        assert result.success is True
        assert result.notification_id == "don:core:notification:123"
        mock_http_client.post.assert_called_once()

    def test_send_notification_with_title(
        self,
        mock_http_client: MagicMock,
        sample_notification_send_response_data: dict[str, Any],
    ) -> None:
        """Test sending a notification with title."""
        mock_http_client.post.return_value = create_mock_response(
            sample_notification_send_response_data
        )

        service = NotificationsService(mock_http_client)
        result = service.send(
            recipient_id="don:identity:user:456",
            message="Your ticket has been updated",
            title="Ticket Update",
        )

        assert isinstance(result, NotificationsSendResponse)
        assert result.success is True
        assert result.notification_id == "don:core:notification:123"
        mock_http_client.post.assert_called_once()

    def test_send_notification_with_channel(
        self,
        mock_http_client: MagicMock,
        sample_notification_send_response_data: dict[str, Any],
    ) -> None:
        """Test sending a notification with specific channel."""
        mock_http_client.post.return_value = create_mock_response(
            sample_notification_send_response_data
        )

        service = NotificationsService(mock_http_client)
        result = service.send(
            recipient_id="don:identity:user:456",
            message="Your ticket has been updated",
            channel="email",
        )

        assert isinstance(result, NotificationsSendResponse)
        assert result.success is True
        assert result.notification_id == "don:core:notification:123"
        mock_http_client.post.assert_called_once()

    def test_send_notification_all_parameters(
        self,
        mock_http_client: MagicMock,
        sample_notification_send_response_data: dict[str, Any],
    ) -> None:
        """Test sending a notification with all parameters."""
        mock_http_client.post.return_value = create_mock_response(
            sample_notification_send_response_data
        )

        service = NotificationsService(mock_http_client)
        result = service.send(
            recipient_id="don:identity:user:456",
            message="Your ticket has been updated",
            title="Ticket Update",
            channel="push",
        )

        assert isinstance(result, NotificationsSendResponse)
        assert result.success is True
        assert result.notification_id == "don:core:notification:123"
        mock_http_client.post.assert_called_once()

    def test_send_notification_failure(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test sending a notification that fails."""
        mock_http_client.post.return_value = create_mock_response(
            {"success": False, "notification_id": None}
        )

        service = NotificationsService(mock_http_client)
        result = service.send(
            recipient_id="don:identity:user:456",
            message="Your ticket has been updated",
        )

        assert isinstance(result, NotificationsSendResponse)
        assert result.success is False
        assert result.notification_id is None
        mock_http_client.post.assert_called_once()


class TestAsyncNotificationsService:
    """Tests for AsyncNotificationsService."""

    @pytest.mark.asyncio
    async def test_send_notification_minimal(
        self,
        mock_async_http_client: AsyncMock,
        sample_notification_send_response_data: dict[str, Any],
    ) -> None:
        """Test sending a notification asynchronously with minimal parameters."""
        mock_async_http_client.post.return_value = create_mock_response(
            sample_notification_send_response_data
        )

        service = AsyncNotificationsService(mock_async_http_client)
        result = await service.send(
            recipient_id="don:identity:user:456",
            message="Your ticket has been updated",
        )

        assert isinstance(result, NotificationsSendResponse)
        assert result.success is True
        assert result.notification_id == "don:core:notification:123"
        mock_async_http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notification_with_title(
        self,
        mock_async_http_client: AsyncMock,
        sample_notification_send_response_data: dict[str, Any],
    ) -> None:
        """Test sending a notification asynchronously with title."""
        mock_async_http_client.post.return_value = create_mock_response(
            sample_notification_send_response_data
        )

        service = AsyncNotificationsService(mock_async_http_client)
        result = await service.send(
            recipient_id="don:identity:user:456",
            message="Your ticket has been updated",
            title="Ticket Update",
        )

        assert isinstance(result, NotificationsSendResponse)
        assert result.success is True
        assert result.notification_id == "don:core:notification:123"
        mock_async_http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notification_with_channel(
        self,
        mock_async_http_client: AsyncMock,
        sample_notification_send_response_data: dict[str, Any],
    ) -> None:
        """Test sending a notification asynchronously with specific channel."""
        mock_async_http_client.post.return_value = create_mock_response(
            sample_notification_send_response_data
        )

        service = AsyncNotificationsService(mock_async_http_client)
        result = await service.send(
            recipient_id="don:identity:user:456",
            message="Your ticket has been updated",
            channel="email",
        )

        assert isinstance(result, NotificationsSendResponse)
        assert result.success is True
        assert result.notification_id == "don:core:notification:123"
        mock_async_http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notification_all_parameters(
        self,
        mock_async_http_client: AsyncMock,
        sample_notification_send_response_data: dict[str, Any],
    ) -> None:
        """Test sending a notification asynchronously with all parameters."""
        mock_async_http_client.post.return_value = create_mock_response(
            sample_notification_send_response_data
        )

        service = AsyncNotificationsService(mock_async_http_client)
        result = await service.send(
            recipient_id="don:identity:user:456",
            message="Your ticket has been updated",
            title="Ticket Update",
            channel="push",
        )

        assert isinstance(result, NotificationsSendResponse)
        assert result.success is True
        assert result.notification_id == "don:core:notification:123"
        mock_async_http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notification_failure(
        self,
        mock_async_http_client: AsyncMock,
    ) -> None:
        """Test sending a notification asynchronously that fails."""
        mock_async_http_client.post.return_value = create_mock_response(
            {"success": False, "notification_id": None}
        )

        service = AsyncNotificationsService(mock_async_http_client)
        result = await service.send(
            recipient_id="don:identity:user:456",
            message="Your ticket has been updated",
        )

        assert isinstance(result, NotificationsSendResponse)
        assert result.success is False
        assert result.notification_id is None
        mock_async_http_client.post.assert_called_once()
