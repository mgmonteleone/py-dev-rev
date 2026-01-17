"""Unit tests for TrackEventsService.

Refs #92
"""

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from devrev.models.track_events import (
    TrackEvent,
    TrackEventsPublishResponse,
)
from devrev.services.track_events import AsyncTrackEventsService, TrackEventsService

from .conftest import create_mock_response


class TestTrackEventsService:
    """Tests for TrackEventsService."""

    def test_publish_single_event(
        self,
        mock_http_client: MagicMock,
        sample_track_events_publish_response_data: dict[str, Any],
    ) -> None:
        """Test publishing a single tracking event."""
        mock_http_client.post.return_value = create_mock_response(
            sample_track_events_publish_response_data
        )

        service = TrackEventsService(mock_http_client)
        events = [
            TrackEvent(
                name="user_login",
                properties={"source": "web"},
                user_id="don:identity:user:123",
            )
        ]
        result = service.publish(events)

        assert isinstance(result, TrackEventsPublishResponse)
        assert result.success is True
        assert result.count == 2
        mock_http_client.post.assert_called_once()

    def test_publish_multiple_events(
        self,
        mock_http_client: MagicMock,
        sample_track_events_publish_response_data: dict[str, Any],
    ) -> None:
        """Test publishing multiple tracking events."""
        mock_http_client.post.return_value = create_mock_response(
            sample_track_events_publish_response_data
        )

        service = TrackEventsService(mock_http_client)
        events = [
            TrackEvent(
                name="user_login",
                properties={"source": "web"},
                user_id="don:identity:user:123",
            ),
            TrackEvent(
                name="page_view",
                properties={"page": "/dashboard"},
                user_id="don:identity:user:123",
            ),
        ]
        result = service.publish(events)

        assert isinstance(result, TrackEventsPublishResponse)
        assert result.success is True
        mock_http_client.post.assert_called_once()

    def test_publish_event_with_timestamp(
        self,
        mock_http_client: MagicMock,
        sample_track_events_publish_response_data: dict[str, Any],
    ) -> None:
        """Test publishing an event with a timestamp."""
        mock_http_client.post.return_value = create_mock_response(
            sample_track_events_publish_response_data
        )

        service = TrackEventsService(mock_http_client)
        timestamp = datetime(2024, 1, 15, 10, 0, 0)
        events = [
            TrackEvent(
                name="user_login",
                timestamp=timestamp,
                user_id="don:identity:user:123",
            )
        ]
        result = service.publish(events)

        assert isinstance(result, TrackEventsPublishResponse)
        assert result.success is True
        mock_http_client.post.assert_called_once()

    def test_publish_event_minimal(
        self,
        mock_http_client: MagicMock,
        sample_track_events_publish_response_data: dict[str, Any],
    ) -> None:
        """Test publishing an event with only required fields."""
        mock_http_client.post.return_value = create_mock_response(
            sample_track_events_publish_response_data
        )

        service = TrackEventsService(mock_http_client)
        events = [TrackEvent(name="button_click")]
        result = service.publish(events)

        assert isinstance(result, TrackEventsPublishResponse)
        assert result.success is True
        mock_http_client.post.assert_called_once()

    def test_publish_event_with_complex_properties(
        self,
        mock_http_client: MagicMock,
        sample_track_events_publish_response_data: dict[str, Any],
    ) -> None:
        """Test publishing an event with complex properties."""
        mock_http_client.post.return_value = create_mock_response(
            sample_track_events_publish_response_data
        )

        service = TrackEventsService(mock_http_client)
        events = [
            TrackEvent(
                name="purchase_completed",
                properties={
                    "items": ["item1", "item2"],
                    "total": 99.99,
                    "currency": "USD",
                    "metadata": {"campaign": "summer_sale"},
                },
                user_id="don:identity:user:456",
            )
        ]
        result = service.publish(events)

        assert isinstance(result, TrackEventsPublishResponse)
        assert result.success is True
        mock_http_client.post.assert_called_once()


class TestAsyncTrackEventsService:
    """Tests for AsyncTrackEventsService."""

    @pytest.mark.asyncio
    async def test_publish_single_event(
        self,
        mock_async_http_client: AsyncMock,
        sample_track_events_publish_response_data: dict[str, Any],
    ) -> None:
        """Test publishing a single tracking event asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response(
            sample_track_events_publish_response_data
        )

        service = AsyncTrackEventsService(mock_async_http_client)
        events = [
            TrackEvent(
                name="user_login",
                properties={"source": "web"},
                user_id="don:identity:user:123",
            )
        ]
        result = await service.publish(events)

        assert isinstance(result, TrackEventsPublishResponse)
        assert result.success is True
        assert result.count == 2
        mock_async_http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_multiple_events(
        self,
        mock_async_http_client: AsyncMock,
        sample_track_events_publish_response_data: dict[str, Any],
    ) -> None:
        """Test publishing multiple tracking events asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response(
            sample_track_events_publish_response_data
        )

        service = AsyncTrackEventsService(mock_async_http_client)
        events = [
            TrackEvent(
                name="user_login",
                properties={"source": "web"},
                user_id="don:identity:user:123",
            ),
            TrackEvent(
                name="page_view",
                properties={"page": "/dashboard"},
                user_id="don:identity:user:123",
            ),
        ]
        result = await service.publish(events)

        assert isinstance(result, TrackEventsPublishResponse)
        assert result.success is True
        mock_async_http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_event_with_timestamp(
        self,
        mock_async_http_client: AsyncMock,
        sample_track_events_publish_response_data: dict[str, Any],
    ) -> None:
        """Test publishing an event with a timestamp asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response(
            sample_track_events_publish_response_data
        )

        service = AsyncTrackEventsService(mock_async_http_client)
        timestamp = datetime(2024, 1, 15, 10, 0, 0)
        events = [
            TrackEvent(
                name="user_login",
                timestamp=timestamp,
                user_id="don:identity:user:123",
            )
        ]
        result = await service.publish(events)

        assert isinstance(result, TrackEventsPublishResponse)
        assert result.success is True
        mock_async_http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_event_minimal(
        self,
        mock_async_http_client: AsyncMock,
        sample_track_events_publish_response_data: dict[str, Any],
    ) -> None:
        """Test publishing an event with only required fields asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response(
            sample_track_events_publish_response_data
        )

        service = AsyncTrackEventsService(mock_async_http_client)
        events = [TrackEvent(name="button_click")]
        result = await service.publish(events)

        assert isinstance(result, TrackEventsPublishResponse)
        assert result.success is True
        mock_async_http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_event_with_complex_properties(
        self,
        mock_async_http_client: AsyncMock,
        sample_track_events_publish_response_data: dict[str, Any],
    ) -> None:
        """Test publishing an event with complex properties asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response(
            sample_track_events_publish_response_data
        )

        service = AsyncTrackEventsService(mock_async_http_client)
        events = [
            TrackEvent(
                name="purchase_completed",
                properties={
                    "items": ["item1", "item2"],
                    "total": 99.99,
                    "currency": "USD",
                    "metadata": {"campaign": "summer_sale"},
                },
                user_id="don:identity:user:456",
            )
        ]
        result = await service.publish(events)

        assert isinstance(result, TrackEventsPublishResponse)
        assert result.success is True
        mock_async_http_client.post.assert_called_once()
