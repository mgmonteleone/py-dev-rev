"""Unit tests for DevRev MCP Server - Engagements Tools."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from devrev.exceptions import DevRevError, NotFoundError, ValidationError
from devrev.models.engagements import EngagementType
from devrev_mcp.tools.engagements import (
    devrev_engagements_count,
    devrev_engagements_create,
    devrev_engagements_delete,
    devrev_engagements_get,
    devrev_engagements_list,
    devrev_engagements_update,
)


def _make_mock_engagement(
    id: str = "eng-123",
    title: str = "Test Engagement",
    engagement_type: EngagementType = EngagementType.MEETING,
    description: str | None = None,
    members: list[str] | None = None,
    parent: str | None = None,
    scheduled_date: datetime | None = None,
    tags: list[str] | None = None,
) -> MagicMock:
    """Create a mock engagement object."""
    engagement = MagicMock()
    engagement.id = id
    engagement.display_id = f"ENG-{id.split('-')[1]}"
    engagement.title = title
    engagement.engagement_type = engagement_type
    engagement.description = description
    engagement.members = members or []
    engagement.parent = parent
    engagement.scheduled_date = scheduled_date
    engagement.tags = tags or []
    engagement.created_date = datetime(2024, 1, 1, 12, 0, 0)
    engagement.modified_date = datetime(2024, 1, 1, 12, 0, 0)
    engagement.model_dump.return_value = {
        "id": id,
        "display_id": engagement.display_id,
        "title": title,
        "engagement_type": engagement_type.value,
        "description": description,
        "members": members or [],
        "parent": parent,
        "scheduled_date": scheduled_date.isoformat() if scheduled_date else None,
        "tags": tags or [],
        "created_date": engagement.created_date.isoformat(),
        "modified_date": engagement.modified_date.isoformat(),
    }
    return engagement


class TestEngagementsListTool:
    """Tests for devrev_engagements_list tool."""

    @pytest.mark.asyncio
    async def test_list_empty(self, mock_ctx, mock_client):
        """Test listing engagements with no results."""
        response = MagicMock()
        response.engagements = []
        response.next_cursor = None
        mock_client.engagements.list.return_value = response

        result = await devrev_engagements_list(mock_ctx)

        assert result["engagements"] == []
        assert result["count"] == 0
        assert "next_cursor" not in result
        mock_client.engagements.list.assert_called_once_with(
            cursor=None,
            limit=25,
            engagement_type=None,
            members=None,
            parent=None,
        )

    @pytest.mark.asyncio
    async def test_list_with_results(self, mock_ctx, mock_client):
        """Test listing engagements with results."""
        engagements = [
            _make_mock_engagement(id="eng-1", title="Meeting 1"),
            _make_mock_engagement(id="eng-2", title="Call 1", engagement_type=EngagementType.CALL),
        ]
        response = MagicMock()
        response.engagements = engagements
        response.next_cursor = None
        mock_client.engagements.list.return_value = response

        result = await devrev_engagements_list(mock_ctx)

        assert result["count"] == 2
        assert len(result["engagements"]) == 2
        assert result["engagements"][0]["id"] == "eng-1"
        assert result["engagements"][1]["id"] == "eng-2"

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, mock_ctx, mock_client):
        """Test listing engagements with pagination."""
        engagements = [_make_mock_engagement(id=f"eng-{i}") for i in range(10)]
        response = MagicMock()
        response.engagements = engagements
        response.next_cursor = "next-page-token"
        mock_client.engagements.list.return_value = response

        result = await devrev_engagements_list(mock_ctx, cursor="current-token", limit=10)

        assert result["count"] == 10
        assert result["next_cursor"] == "next-page-token"
        mock_client.engagements.list.assert_called_once_with(
            cursor="current-token",
            limit=10,
            engagement_type=None,
            members=None,
            parent=None,
        )

    @pytest.mark.asyncio
    async def test_list_with_filters(self, mock_ctx, mock_client):
        """Test listing engagements with filters."""
        engagements = [_make_mock_engagement(engagement_type=EngagementType.MEETING)]
        response = MagicMock()
        response.engagements = engagements
        response.next_cursor = None
        mock_client.engagements.list.return_value = response

        result = await devrev_engagements_list(
            mock_ctx,
            engagement_type=["meeting", "call"],
            members=["user-1", "user-2"],
            parent="work-123",
        )

        assert result["count"] == 1
        mock_client.engagements.list.assert_called_once_with(
            cursor=None,
            limit=25,
            engagement_type=[EngagementType.MEETING, EngagementType.CALL],
            members=["user-1", "user-2"],
            parent="work-123",
        )

    @pytest.mark.asyncio
    async def test_list_error(self, mock_ctx, mock_client):
        """Test listing engagements with error."""
        mock_client.engagements.list.side_effect = DevRevError("API error")

        with pytest.raises(RuntimeError, match="API error"):
            await devrev_engagements_list(mock_ctx)


class TestEngagementsGetTool:
    """Tests for devrev_engagements_get tool."""

    @pytest.mark.asyncio
    async def test_get_success(self, mock_ctx, mock_client):
        """Test getting an engagement successfully."""
        engagement = _make_mock_engagement(id="eng-123", title="Test Meeting")
        mock_client.engagements.get.return_value = engagement

        result = await devrev_engagements_get(mock_ctx, id="eng-123")

        assert result["id"] == "eng-123"
        assert result["title"] == "Test Meeting"
        mock_client.engagements.get.assert_called_once_with("eng-123")

    @pytest.mark.asyncio
    async def test_get_not_found(self, mock_ctx, mock_client):
        """Test getting a non-existent engagement."""
        mock_client.engagements.get.side_effect = NotFoundError("Engagement not found")

        with pytest.raises(RuntimeError, match="Engagement not found"):
            await devrev_engagements_get(mock_ctx, id="eng-999")


class TestEngagementsCreateTool:
    """Tests for devrev_engagements_create tool."""

    @pytest.mark.asyncio
    async def test_create_minimal(self, mock_ctx, mock_client):
        """Test creating an engagement with minimal fields."""
        engagement = _make_mock_engagement(id="eng-new", title="New Meeting")
        mock_client.engagements.create.return_value = engagement

        result = await devrev_engagements_create(
            mock_ctx,
            title="New Meeting",
            engagement_type="meeting",
        )

        assert result["id"] == "eng-new"
        assert result["title"] == "New Meeting"
        mock_client.engagements.create.assert_called_once_with(
            title="New Meeting",
            engagement_type=EngagementType.MEETING,
            description=None,
            members=None,
            parent=None,
            scheduled_date=None,
            tags=None,
        )

    @pytest.mark.asyncio
    async def test_create_full_with_scheduled_date(self, mock_ctx, mock_client):
        """Test creating an engagement with all fields including scheduled date."""
        scheduled = datetime(2024, 6, 15, 14, 30, 0)
        engagement = _make_mock_engagement(
            id="eng-full",
            title="Full Meeting",
            description="Detailed description",
            members=["user-1", "user-2"],
            parent="work-123",
            scheduled_date=scheduled,
            tags=["important", "customer"],
        )
        mock_client.engagements.create.return_value = engagement

        result = await devrev_engagements_create(
            mock_ctx,
            title="Full Meeting",
            engagement_type="meeting",
            description="Detailed description",
            members=["user-1", "user-2"],
            parent="work-123",
            scheduled_date="2024-06-15T14:30:00",
            tags=["important", "customer"],
        )

        assert result["id"] == "eng-full"
        mock_client.engagements.create.assert_called_once_with(
            title="Full Meeting",
            engagement_type=EngagementType.MEETING,
            description="Detailed description",
            members=["user-1", "user-2"],
            parent="work-123",
            scheduled_date=scheduled,
            tags=["important", "customer"],
        )

    @pytest.mark.asyncio
    async def test_create_error(self, mock_ctx, mock_client):
        """Test creating an engagement with validation error."""
        mock_client.engagements.create.side_effect = ValidationError("Invalid engagement type")

        with pytest.raises(RuntimeError, match="Invalid engagement type"):
            await devrev_engagements_create(
                mock_ctx,
                title="Bad Meeting",
                engagement_type="meeting",
            )


class TestEngagementsUpdateTool:
    """Tests for devrev_engagements_update tool."""

    @pytest.mark.asyncio
    async def test_update_success(self, mock_ctx, mock_client):
        """Test updating an engagement successfully."""
        updated = _make_mock_engagement(
            id="eng-123",
            title="Updated Title",
            description="Updated description",
        )
        mock_client.engagements.update.return_value = updated

        result = await devrev_engagements_update(
            mock_ctx,
            id="eng-123",
            title="Updated Title",
            description="Updated description",
            engagement_type="call",
        )

        assert result["id"] == "eng-123"
        assert result["title"] == "Updated Title"
        mock_client.engagements.update.assert_called_once_with(
            "eng-123",
            title="Updated Title",
            description="Updated description",
            engagement_type=EngagementType.CALL,
            scheduled_date=None,
        )

    @pytest.mark.asyncio
    async def test_update_error(self, mock_ctx, mock_client):
        """Test updating an engagement with error."""
        mock_client.engagements.update.side_effect = NotFoundError("Engagement not found")

        with pytest.raises(RuntimeError, match="Engagement not found"):
            await devrev_engagements_update(mock_ctx, id="eng-999", title="New Title")


class TestEngagementsDeleteTool:
    """Tests for devrev_engagements_delete tool."""

    @pytest.mark.asyncio
    async def test_delete_success(self, mock_ctx, mock_client):
        """Test deleting an engagement successfully."""
        mock_client.engagements.delete.return_value = None

        result = await devrev_engagements_delete(mock_ctx, id="eng-123")

        assert result["deleted"] is True
        assert result["id"] == "eng-123"
        mock_client.engagements.delete.assert_called_once_with("eng-123")

    @pytest.mark.asyncio
    async def test_delete_not_found(self, mock_ctx, mock_client):
        """Test deleting a non-existent engagement."""
        mock_client.engagements.delete.side_effect = NotFoundError("Engagement not found")

        with pytest.raises(RuntimeError, match="Engagement not found"):
            await devrev_engagements_delete(mock_ctx, id="eng-999")


class TestEngagementsCountTool:
    """Tests for devrev_engagements_count tool."""

    @pytest.mark.asyncio
    async def test_count_success(self, mock_ctx, mock_client):
        """Test counting engagements successfully."""
        mock_client.engagements.count.return_value = 42

        result = await devrev_engagements_count(mock_ctx)

        assert result["count"] == 42
        mock_client.engagements.count.assert_called_once_with(
            engagement_type=None,
            members=None,
        )

    @pytest.mark.asyncio
    async def test_count_with_filters(self, mock_ctx, mock_client):
        """Test counting engagements with filters."""
        mock_client.engagements.count.return_value = 15

        result = await devrev_engagements_count(
            mock_ctx,
            engagement_type=["meeting", "call"],
            members=["user-1"],
        )

        assert result["count"] == 15
        mock_client.engagements.count.assert_called_once_with(
            engagement_type=[EngagementType.MEETING, EngagementType.CALL],
            members=["user-1"],
        )

    @pytest.mark.asyncio
    async def test_count_error(self, mock_ctx, mock_client):
        """Test counting engagements with error."""
        mock_client.engagements.count.side_effect = DevRevError("API error")

        with pytest.raises(RuntimeError, match="API error"):
            await devrev_engagements_count(mock_ctx)
