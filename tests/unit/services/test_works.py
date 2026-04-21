"""Unit tests for WorksService."""

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from devrev.models.works import (
    IssuePriority,
    Work,
    WorksListResponse,
    WorkType,
)
from devrev.services.works import (
    AsyncWorksService,
    WorksService,
    _is_before_cutoff,
    _normalize_sort_by,
)


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
        mock_http_client.post.return_value = create_mock_response({"work": sample_work_data})

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
        mock_http_client.post.return_value = create_mock_response({"work": sample_work_data})

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
        mock_http_client.post.return_value = create_mock_response({"works": [sample_work_data]})

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
        mock_http_client.post.return_value = create_mock_response({"works": [sample_work_data]})

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
        mock_http_client.post.return_value = create_mock_response({"work": sample_work_data})

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
        mock_http_client.post.return_value = create_mock_response({"work": sample_work_data})

        service = WorksService(mock_http_client)
        result = service.create(
            title="Urgent Issue",
            applies_to_part="don:core:part:456",
            type=WorkType.ISSUE,
            priority=IssuePriority.P1,
            owned_by=["don:identity:user:789"],
        )

        assert isinstance(result, Work)

    def test_work_with_applies_to_part_as_object(
        self,
        mock_http_client: MagicMock,
        sample_work_data: dict[str, Any],
    ) -> None:
        """Test that applies_to_part can be an object (as returned by the API).

        The DevRev API returns applies_to_part as a PartSummary object in responses,
        not just a string ID. This test validates that the model correctly parses
        the object format.
        """
        sample_work_data["applies_to_part"] = {
            "type": "product",
            "display_id": "PROD-1",
            "id": "don:core:dvrv-us-1:devo/org123:product/1",
            "name": "Test Product",
            "state": "active",
            "owned_by": [
                {
                    "type": "sys_user",
                    "display_id": "SYSU-1",
                    "display_name": "devrev-bot",
                    "full_name": "DevRev Bot",
                    "id": "don:identity:dvrv-us-1:devo/org123:sysu/1",
                }
            ],
        }
        mock_http_client.post.return_value = create_mock_response({"work": sample_work_data})

        service = WorksService(mock_http_client)
        result = service.get("don:core:issue:123")

        assert isinstance(result, Work)
        assert result.applies_to_part is not None
        # The applies_to_part should be parsed as a PartSummary object
        from devrev.models.parts import PartSummary

        assert isinstance(result.applies_to_part, PartSummary)
        assert result.applies_to_part.id == "don:core:dvrv-us-1:devo/org123:product/1"
        assert result.applies_to_part.name == "Test Product"
        assert result.applies_to_part.type == "product"
        assert result.applies_to_part.display_id == "PROD-1"
        assert result.applies_to_part.state == "active"
        # Verify owned_by is parsed correctly
        assert result.applies_to_part.owned_by is not None
        assert isinstance(result.applies_to_part.owned_by, list)
        assert len(result.applies_to_part.owned_by) == 1
        assert result.applies_to_part.owned_by[0].id == "don:identity:dvrv-us-1:devo/org123:sysu/1"

    def test_work_with_applies_to_part_as_string(
        self,
        mock_http_client: MagicMock,
        sample_work_data: dict[str, Any],
    ) -> None:
        """Test that applies_to_part can also be a string (backward compatibility)."""
        sample_work_data["applies_to_part"] = "don:core:dvrv-us-1:devo/org123:product/1"
        mock_http_client.post.return_value = create_mock_response({"work": sample_work_data})

        service = WorksService(mock_http_client)
        result = service.get("don:core:issue:123")

        assert isinstance(result, Work)
        assert result.applies_to_part == "don:core:dvrv-us-1:devo/org123:product/1"


def _work_page(works: list[dict[str, Any]], next_cursor: str | None = None) -> dict[str, Any]:
    """Build a works.list response payload for mocking."""
    return {"works": works, "next_cursor": next_cursor}


def _work_record(work_id: str, timestamp_field: str, timestamp: str) -> dict[str, Any]:
    """Build a single work dict with a specific timestamp field set."""
    return {
        "id": work_id,
        "type": "issue",
        "display_id": work_id.split(":")[-1],
        "title": f"Work {work_id}",
        timestamp_field: timestamp,
    }


class TestNormalizeSortBy:
    """Tests for the ``_normalize_sort_by`` helper."""

    def test_none_passes_through(self) -> None:
        assert _normalize_sort_by(None) is None

    def test_empty_list(self) -> None:
        assert _normalize_sort_by([]) == []

    def test_dash_prefix_becomes_desc(self) -> None:
        assert _normalize_sort_by(["-modified_date"]) == ["modified_date:desc"]

    def test_bare_field_becomes_asc(self) -> None:
        assert _normalize_sort_by(["modified_date"]) == ["modified_date:asc"]

    def test_server_form_passes_through(self) -> None:
        assert _normalize_sort_by(["modified_date:desc"]) == ["modified_date:desc"]
        assert _normalize_sort_by(["created_date:asc"]) == ["created_date:asc"]

    def test_mixed_inputs(self) -> None:
        assert _normalize_sort_by(["-modified_date", "created_date:asc", "title"]) == [
            "modified_date:desc",
            "created_date:asc",
            "title:asc",
        ]


class TestWorksServiceSortNormalization:
    """Sort normalization is applied inside list() and export() requests."""

    def test_list_normalizes_dash_form(
        self, mock_http_client: MagicMock, sample_work_data: dict[str, Any]
    ) -> None:
        mock_http_client.post.return_value = create_mock_response(_work_page([sample_work_data]))
        service = WorksService(mock_http_client)
        service.list(sort_by=["-modified_date"])

        _, kwargs = mock_http_client.post.call_args
        assert kwargs["data"]["sort_by"] == ["modified_date:desc"]

    def test_list_preserves_server_form(
        self, mock_http_client: MagicMock, sample_work_data: dict[str, Any]
    ) -> None:
        mock_http_client.post.return_value = create_mock_response(_work_page([sample_work_data]))
        service = WorksService(mock_http_client)
        service.list(sort_by=["modified_date:desc"])

        _, kwargs = mock_http_client.post.call_args
        assert kwargs["data"]["sort_by"] == ["modified_date:desc"]

    def test_export_normalizes_sort_by(
        self, mock_http_client: MagicMock, sample_work_data: dict[str, Any]
    ) -> None:
        mock_http_client.post.return_value = create_mock_response({"works": [sample_work_data]})
        service = WorksService(mock_http_client)
        service.export(sort_by=["-created_date"])

        _, kwargs = mock_http_client.post.call_args
        assert kwargs["data"]["sort_by"] == ["created_date:desc"]


class TestListModifiedSince:
    """Tests for ``WorksService.list_modified_since``."""

    def test_early_exit_when_record_older_than_after(self, mock_http_client: MagicMock) -> None:
        """Iteration stops as soon as a record's modified_date < after."""
        after = datetime(2024, 6, 1, tzinfo=UTC)
        page1 = _work_page(
            [
                _work_record("don:core:work:1", "modified_date", "2024-07-01T00:00:00Z"),
                _work_record("don:core:work:2", "modified_date", "2024-06-15T00:00:00Z"),
                _work_record("don:core:work:3", "modified_date", "2024-05-15T00:00:00Z"),
            ],
            next_cursor="cursor-2",
        )
        mock_http_client.post.return_value = create_mock_response(page1)

        service = WorksService(mock_http_client)
        results = service.list_modified_since(after)

        assert [w.id for w in results] == ["don:core:work:1", "don:core:work:2"]
        # Only one HTTP request — early-exit prevented a second page fetch.
        assert mock_http_client.post.call_count == 1
        _, kwargs = mock_http_client.post.call_args
        assert kwargs["data"]["sort_by"] == ["modified_date:desc"]

    def test_paginates_until_cutoff_across_pages(self, mock_http_client: MagicMock) -> None:
        after = datetime(2024, 6, 1, tzinfo=UTC)
        page1 = _work_page(
            [
                _work_record("don:core:work:1", "modified_date", "2024-07-01T00:00:00Z"),
                _work_record("don:core:work:2", "modified_date", "2024-06-15T00:00:00Z"),
            ],
            next_cursor="cursor-2",
        )
        page2 = _work_page(
            [
                _work_record("don:core:work:3", "modified_date", "2024-06-05T00:00:00Z"),
                _work_record("don:core:work:4", "modified_date", "2024-05-15T00:00:00Z"),
            ],
            next_cursor="cursor-3",
        )
        mock_http_client.post.side_effect = [
            create_mock_response(page1),
            create_mock_response(page2),
        ]

        service = WorksService(mock_http_client)
        results = service.list_modified_since(after)

        assert [w.id for w in results] == [
            "don:core:work:1",
            "don:core:work:2",
            "don:core:work:3",
        ]
        assert mock_http_client.post.call_count == 2

    def test_respects_hard_limit(self, mock_http_client: MagicMock) -> None:
        after = datetime(2020, 1, 1, tzinfo=UTC)
        page = _work_page(
            [
                _work_record("don:core:work:1", "modified_date", "2024-07-01T00:00:00Z"),
                _work_record("don:core:work:2", "modified_date", "2024-06-01T00:00:00Z"),
                _work_record("don:core:work:3", "modified_date", "2024-05-01T00:00:00Z"),
            ],
            next_cursor="cursor-2",
        )
        mock_http_client.post.return_value = create_mock_response(page)

        service = WorksService(mock_http_client)
        results = service.list_modified_since(after, limit=2)

        assert [w.id for w in results] == ["don:core:work:1", "don:core:work:2"]
        assert mock_http_client.post.call_count == 1


class TestListCreatedSince:
    """Tests for ``WorksService.list_created_since``."""

    def test_early_exit_and_sort_order(self, mock_http_client: MagicMock) -> None:
        after = datetime(2024, 6, 1, tzinfo=UTC)
        page = _work_page(
            [
                _work_record("don:core:work:1", "created_date", "2024-07-01T00:00:00Z"),
                _work_record("don:core:work:2", "created_date", "2024-05-15T00:00:00Z"),
            ]
        )
        mock_http_client.post.return_value = create_mock_response(page)

        service = WorksService(mock_http_client)
        results = service.list_created_since(after)

        assert [w.id for w in results] == ["don:core:work:1"]
        _, kwargs = mock_http_client.post.call_args
        assert kwargs["data"]["sort_by"] == ["created_date:desc"]

    def test_respects_hard_limit(self, mock_http_client: MagicMock) -> None:
        after = datetime(2020, 1, 1, tzinfo=UTC)
        page = _work_page(
            [
                _work_record("don:core:work:1", "created_date", "2024-07-01T00:00:00Z"),
                _work_record("don:core:work:2", "created_date", "2024-06-01T00:00:00Z"),
            ],
            next_cursor="cursor-2",
        )
        mock_http_client.post.return_value = create_mock_response(page)

        service = WorksService(mock_http_client)
        results = service.list_created_since(after, limit=1)

        assert [w.id for w in results] == ["don:core:work:1"]
        assert mock_http_client.post.call_count == 1


class TestAsyncListSince:
    """Async variants for ``list_modified_since`` / ``list_created_since``."""

    @pytest.mark.asyncio
    async def test_async_list_modified_since_early_exit(self) -> None:
        after = datetime(2024, 6, 1, tzinfo=UTC)
        page = _work_page(
            [
                _work_record("don:core:work:1", "modified_date", "2024-07-01T00:00:00Z"),
                _work_record("don:core:work:2", "modified_date", "2024-05-15T00:00:00Z"),
            ],
            next_cursor="cursor-next",
        )
        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = create_mock_response(page)

        service = AsyncWorksService(mock_async_client)
        results = await service.list_modified_since(after)

        assert [w.id for w in results] == ["don:core:work:1"]
        assert mock_async_client.post.call_count == 1
        _, kwargs = mock_async_client.post.call_args
        assert kwargs["data"]["sort_by"] == ["modified_date:desc"]

    @pytest.mark.asyncio
    async def test_async_list_created_since_respects_limit(self) -> None:
        after = datetime(2020, 1, 1, tzinfo=UTC)
        page = _work_page(
            [
                _work_record("don:core:work:1", "created_date", "2024-07-01T00:00:00Z"),
                _work_record("don:core:work:2", "created_date", "2024-06-01T00:00:00Z"),
                _work_record("don:core:work:3", "created_date", "2024-05-01T00:00:00Z"),
            ],
            next_cursor="cursor-next",
        )
        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = create_mock_response(page)

        service = AsyncWorksService(mock_async_client)
        results = await service.list_created_since(after, limit=2)

        assert [w.id for w in results] == ["don:core:work:1", "don:core:work:2"]
        assert mock_async_client.post.call_count == 1

    @pytest.mark.asyncio
    async def test_async_list_normalizes_sort_by(self) -> None:
        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = create_mock_response(
            {"works": [], "next_cursor": None}
        )

        service = AsyncWorksService(mock_async_client)
        await service.list(sort_by=["-modified_date"])

        _, kwargs = mock_async_client.post.call_args
        assert kwargs["data"]["sort_by"] == ["modified_date:desc"]


class TestIsBeforeCutoffHelper:
    """Tests for the ``_is_before_cutoff`` helper."""

    def test_none_timestamp_returns_false(self) -> None:
        cutoff = datetime(2024, 6, 1, tzinfo=UTC)
        assert _is_before_cutoff(None, cutoff) is False

    def test_aware_timestamp_before_cutoff(self) -> None:
        cutoff = datetime(2024, 6, 1, tzinfo=UTC)
        ts = datetime(2024, 5, 1, tzinfo=UTC)
        assert _is_before_cutoff(ts, cutoff) is True

    def test_aware_timestamp_after_cutoff(self) -> None:
        cutoff = datetime(2024, 6, 1, tzinfo=UTC)
        ts = datetime(2024, 7, 1, tzinfo=UTC)
        assert _is_before_cutoff(ts, cutoff) is False

    def test_naive_timestamp_with_aware_cutoff_returns_false(self) -> None:
        """Incompatible tz-awareness must not raise; defers to server filter."""
        cutoff = datetime(2024, 6, 1, tzinfo=UTC)
        ts = datetime(2024, 5, 1)  # naive
        assert _is_before_cutoff(ts, cutoff) is False

    def test_aware_timestamp_with_naive_cutoff_returns_false(self) -> None:
        """Incompatible tz-awareness must not raise; defers to server filter."""
        cutoff = datetime(2024, 6, 1)  # naive
        ts = datetime(2024, 5, 1, tzinfo=UTC)
        assert _is_before_cutoff(ts, cutoff) is False


class TestListSinceTimestampTypeSafety:
    """``_list_since`` must not raise TypeError on mixed naive/aware timestamps."""

    def test_naive_after_with_aware_record_timestamps_does_not_raise(
        self, mock_http_client: MagicMock
    ) -> None:
        """A naive ``after`` with tz-aware record timestamps must not raise."""
        after = datetime(2024, 6, 1)  # naive
        page = _work_page(
            [
                _work_record("don:core:work:1", "modified_date", "2024-07-01T00:00:00Z"),
                _work_record("don:core:work:2", "modified_date", "2024-05-15T00:00:00Z"),
            ],
            next_cursor=None,
        )
        mock_http_client.post.return_value = create_mock_response(page)

        service = WorksService(mock_http_client)
        # Must not raise TypeError. Both records are kept because the helper
        # returns False on incompatible tz-awareness (server-side filter is
        # authoritative).
        results = service.list_modified_since(after)

        assert [w.id for w in results] == ["don:core:work:1", "don:core:work:2"]
        assert mock_http_client.post.call_count == 1

    def test_aware_after_with_naive_record_timestamps_does_not_raise(
        self, mock_http_client: MagicMock
    ) -> None:
        """A tz-aware ``after`` with naive record timestamps must not raise."""
        after = datetime(2024, 6, 1, tzinfo=UTC)
        # Timestamps without 'Z' / offset are parsed as naive datetimes.
        page = _work_page(
            [
                _work_record("don:core:work:1", "modified_date", "2024-07-01T00:00:00"),
                _work_record("don:core:work:2", "modified_date", "2024-05-15T00:00:00"),
            ],
            next_cursor=None,
        )
        mock_http_client.post.return_value = create_mock_response(page)

        service = WorksService(mock_http_client)
        results = service.list_modified_since(after)

        assert [w.id for w in results] == ["don:core:work:1", "don:core:work:2"]
        assert mock_http_client.post.call_count == 1

    @pytest.mark.asyncio
    async def test_async_naive_after_with_aware_record_timestamps_does_not_raise(
        self,
    ) -> None:
        """Async variant: naive ``after`` with aware record timestamps must not raise."""
        after = datetime(2024, 6, 1)  # naive
        page = _work_page(
            [
                _work_record("don:core:work:1", "created_date", "2024-07-01T00:00:00Z"),
                _work_record("don:core:work:2", "created_date", "2024-05-15T00:00:00Z"),
            ],
            next_cursor=None,
        )
        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = create_mock_response(page)

        service = AsyncWorksService(mock_async_client)
        results = await service.list_created_since(after)

        assert [w.id for w in results] == ["don:core:work:1", "don:core:work:2"]
        assert mock_async_client.post.call_count == 1
