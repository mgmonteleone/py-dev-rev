"""Unit tests for WorksService."""

from typing import Any
from unittest.mock import MagicMock

import httpx
import pytest

from devrev.models.works import (
    IssuePriority,
    Work,
    WorksListResponse,
    WorkType,
)
from devrev.services.works import WorksService


def create_mock_response(data: dict[str, Any], status_code: int = 200) -> MagicMock:
    """Create a mock HTTP response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.is_success = 200 <= status_code < 300
    response.json.return_value = data
    return response


@pytest.fixture
def mock_http_client() -> MagicMock:
    """Create a mock HTTP client."""
    return MagicMock()


@pytest.fixture
def sample_work_data() -> dict[str, Any]:
    """Sample work data for testing."""
    return {
        "id": "don:core:issue:123",
        "type": "issue",
        "display_id": "ISS-123",
        "title": "Test Issue",
        "body": "Test issue body",
        "created_date": "2024-01-15T10:00:00Z",
    }


class TestWorksService:
    """Tests for WorksService."""

    def test_create_work(
        self,
        mock_http_client: MagicMock,
        sample_work_data: dict[str, Any],
    ) -> None:
        """Test creating a work item."""
        mock_http_client.post.return_value = create_mock_response(
            {"work": sample_work_data}
        )

        service = WorksService(mock_http_client)
        result = service.create(
            title="Test Issue",
            applies_to_part="don:core:part:456",
            type=WorkType.ISSUE,
            owned_by=["don:identity:user:789"],
        )

        assert isinstance(result, Work)
        assert result.id == "don:core:issue:123"
        assert result.title == "Test Issue"

    def test_get_work(
        self,
        mock_http_client: MagicMock,
        sample_work_data: dict[str, Any],
    ) -> None:
        """Test getting a work item by ID."""
        mock_http_client.post.return_value = create_mock_response(
            {"work": sample_work_data}
        )

        service = WorksService(mock_http_client)
        result = service.get("don:core:issue:123")

        assert isinstance(result, Work)
        assert result.id == "don:core:issue:123"

    def test_list_works(
        self,
        mock_http_client: MagicMock,
        sample_work_data: dict[str, Any],
    ) -> None:
        """Test listing work items."""
        mock_http_client.post.return_value = create_mock_response(
            {"works": [sample_work_data]}
        )

        service = WorksService(mock_http_client)
        result = service.list()

        assert isinstance(result, WorksListResponse)
        assert len(result.works) == 1
        assert isinstance(result.works[0], Work)

    def test_list_works_with_filters(
        self,
        mock_http_client: MagicMock,
        sample_work_data: dict[str, Any],
    ) -> None:
        """Test listing work items with filters."""
        mock_http_client.post.return_value = create_mock_response(
            {"works": [sample_work_data]}
        )

        service = WorksService(mock_http_client)
        result = service.list(type=[WorkType.ISSUE], limit=10)

        assert isinstance(result, WorksListResponse)
        mock_http_client.post.assert_called_once()

    def test_update_work(
        self,
        mock_http_client: MagicMock,
        sample_work_data: dict[str, Any],
    ) -> None:
        """Test updating a work item."""
        sample_work_data["title"] = "Updated Title"
        mock_http_client.post.return_value = create_mock_response(
            {"work": sample_work_data}
        )

        service = WorksService(mock_http_client)
        result = service.update("don:core:issue:123", title="Updated Title")

        assert isinstance(result, Work)
        assert result.title == "Updated Title"

    def test_create_work_with_priority(
        self,
        mock_http_client: MagicMock,
        sample_work_data: dict[str, Any],
    ) -> None:
        """Test creating a work item with priority."""
        sample_work_data["priority"] = "p1"
        mock_http_client.post.return_value = create_mock_response(
            {"work": sample_work_data}
        )

        service = WorksService(mock_http_client)
        result = service.create(
            title="Urgent Issue",
            applies_to_part="don:core:part:456",
            type=WorkType.ISSUE,
            priority=IssuePriority.P1,
            owned_by=["don:identity:user:789"],
        )

        assert isinstance(result, Work)

