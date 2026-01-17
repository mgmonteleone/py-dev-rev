"""Unit tests for EngagementsService."""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.engagements import Engagement, EngagementType
from devrev.services.engagements import EngagementsService

from .conftest import create_mock_response


class TestEngagementsService:
    """Tests for EngagementsService."""

    def test_create_engagement(
        self,
        mock_http_client: MagicMock,
        sample_engagement_data: dict[str, Any],
    ) -> None:
        """Test creating an engagement."""
        mock_http_client.post.return_value = create_mock_response(
            {"engagement": sample_engagement_data}
        )

        service = EngagementsService(mock_http_client)
        result = service.create(
            title="Test Engagement",
            engagement_type=EngagementType.MEETING,
            description="Test engagement description",
            members=["don:identity:user:456"],
            scheduled_date=None,
            tags=["don:core:tag:789"],
        )

        assert isinstance(result, Engagement)
        assert result.id == "don:core:engagement:123"
        assert result.title == "Test Engagement"
        assert result.engagement_type == EngagementType.MEETING
        mock_http_client.post.assert_called_once()

    def test_get_engagement(
        self,
        mock_http_client: MagicMock,
        sample_engagement_data: dict[str, Any],
    ) -> None:
        """Test getting an engagement by ID."""
        mock_http_client.post.return_value = create_mock_response(
            {"engagement": sample_engagement_data}
        )

        service = EngagementsService(mock_http_client)
        result = service.get(id="don:core:engagement:123")

        assert isinstance(result, Engagement)
        assert result.id == "don:core:engagement:123"
        assert result.title == "Test Engagement"
        mock_http_client.post.assert_called_once()

    def test_list_engagements(
        self,
        mock_http_client: MagicMock,
        sample_engagement_data: dict[str, Any],
    ) -> None:
        """Test listing engagements."""
        mock_http_client.post.return_value = create_mock_response(
            {"engagements": [sample_engagement_data]}
        )

        service = EngagementsService(mock_http_client)
        result = service.list()

        assert len(result.engagements) == 1
        assert isinstance(result.engagements[0], Engagement)
        assert result.engagements[0].id == "don:core:engagement:123"
        mock_http_client.post.assert_called_once()

    def test_list_engagements_with_filters(
        self,
        mock_http_client: MagicMock,
        sample_engagement_data: dict[str, Any],
    ) -> None:
        """Test listing engagements with filters."""
        mock_http_client.post.return_value = create_mock_response(
            {"engagements": [sample_engagement_data], "next_cursor": "next-cursor"}
        )

        service = EngagementsService(mock_http_client)
        result = service.list(
            cursor="cursor-123",
            limit=50,
            engagement_type=[EngagementType.MEETING, EngagementType.CALL],
            members=["don:identity:user:456"],
            parent="don:core:engagement:999",
        )

        assert len(result.engagements) == 1
        assert result.next_cursor == "next-cursor"
        mock_http_client.post.assert_called_once()

    def test_list_engagements_empty(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test listing engagements returns empty list."""
        mock_http_client.post.return_value = create_mock_response({"engagements": []})

        service = EngagementsService(mock_http_client)
        result = service.list()

        assert len(result.engagements) == 0
        mock_http_client.post.assert_called_once()

    def test_update_engagement(
        self,
        mock_http_client: MagicMock,
        sample_engagement_data: dict[str, Any],
    ) -> None:
        """Test updating an engagement."""
        updated_data = {**sample_engagement_data, "title": "Updated Engagement"}
        mock_http_client.post.return_value = create_mock_response({"engagement": updated_data})

        service = EngagementsService(mock_http_client)
        result = service.update(
            id="don:core:engagement:123",
            title="Updated Engagement",
            description="Updated description",
        )

        assert isinstance(result, Engagement)
        assert result.title == "Updated Engagement"
        mock_http_client.post.assert_called_once()

    def test_delete_engagement(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test deleting an engagement."""
        mock_http_client.post.return_value = create_mock_response({})

        service = EngagementsService(mock_http_client)
        result = service.delete(id="don:core:engagement:123")

        assert result is None
        mock_http_client.post.assert_called_once()

    def test_count_engagements(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test counting engagements."""
        mock_http_client.post.return_value = create_mock_response({"count": 42})

        service = EngagementsService(mock_http_client)
        result = service.count(
            engagement_type=[EngagementType.MEETING],
            members=["don:identity:user:456"],
        )

        assert result == 42
        mock_http_client.post.assert_called_once()
