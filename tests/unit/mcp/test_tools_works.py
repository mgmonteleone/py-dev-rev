"""Comprehensive tests for DevRev MCP works tools."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from devrev_mcp.tools.works import (
    devrev_works_count,
    devrev_works_create,
    devrev_works_delete,
    devrev_works_export,
    devrev_works_get,
    devrev_works_list,
    devrev_works_list_created_since,
    devrev_works_list_modified_since,
    devrev_works_update,
)


def _make_mock_work(data: dict[str, str] | None = None) -> MagicMock:
    """Create a mock Work model with model_dump support."""
    default = {"id": "don:core:work/1", "title": "Test Work", "type": "ticket"}
    work = MagicMock()
    work.model_dump.return_value = {**(data or default)}
    return work


class TestWorksListTool:
    """Tests for devrev_works_list tool."""

    async def test_list_returns_paginated_response(self, mock_ctx, mock_client):
        """Test list returns paginated response with works."""
        work = _make_mock_work()
        response = MagicMock()
        response.works = [work]
        response.next_cursor = None
        mock_client.works.list.return_value = response

        result = await devrev_works_list(mock_ctx)
        assert result["count"] == 1
        assert "works" in result
        assert "next_cursor" not in result

    async def test_list_with_cursor(self, mock_ctx, mock_client):
        """Test list with pagination cursor."""
        work = _make_mock_work()
        response = MagicMock()
        response.works = [work]
        response.next_cursor = "cursor123"
        mock_client.works.list.return_value = response

        result = await devrev_works_list(mock_ctx, cursor="prev_cursor")
        assert result["next_cursor"] == "cursor123"
        mock_client.works.list.assert_called_once()

    async def test_list_with_type_filter(self, mock_ctx, mock_client):
        """Test list with work type filter."""
        response = MagicMock()
        response.works = []
        response.next_cursor = None
        mock_client.works.list.return_value = response

        await devrev_works_list(mock_ctx, type=["ticket", "issue"])
        call_kwargs = mock_client.works.list.call_args.kwargs
        # type parameter should be converted to WorkType enums
        from devrev.models.works import WorkType

        assert call_kwargs["type"] == [WorkType.TICKET, WorkType.ISSUE]

    async def test_list_clamps_page_size(self, mock_ctx, mock_client):
        """Test list clamps page size to maximum."""
        response = MagicMock()
        response.works = []
        response.next_cursor = None
        mock_client.works.list.return_value = response

        await devrev_works_list(mock_ctx, limit=500)
        call_kwargs = mock_client.works.list.call_args.kwargs
        assert call_kwargs["limit"] == 100  # clamped to max

    async def test_list_error_raises_runtime_error(self, mock_ctx, mock_client):
        """Test list raises RuntimeError on API error."""
        from devrev.exceptions import NotFoundError

        mock_client.works.list.side_effect = NotFoundError("not found")

        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_works_list(mock_ctx)


class TestWorksGetTool:
    """Tests for devrev_works_get tool."""

    async def test_get_returns_serialized_work(self, mock_ctx, mock_client):
        """Test get returns serialized work item."""
        work = _make_mock_work({"id": "w1", "title": "My Work"})
        mock_client.works.get.return_value = work

        result = await devrev_works_get(mock_ctx, id="w1")
        assert result["id"] == "w1"
        assert result["title"] == "My Work"

    async def test_get_not_found_raises(self, mock_ctx, mock_client):
        """Test get raises RuntimeError when work not found."""
        from devrev.exceptions import NotFoundError

        mock_client.works.get.side_effect = NotFoundError("Work not found")

        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_works_get(mock_ctx, id="nonexistent")


class TestWorksCreateTool:
    """Tests for devrev_works_create tool."""

    async def test_create_with_required_fields(self, mock_ctx, mock_client):
        """Test create with required fields only."""
        work = _make_mock_work({"id": "w2", "title": "New", "type": "ticket"})
        mock_client.works.create.return_value = work

        result = await devrev_works_create(
            mock_ctx,
            title="New",
            applies_to_part="part1",
            type="ticket",
            owned_by=["user1"],
        )
        assert result["id"] == "w2"
        from devrev.models.works import WorkType

        call_kwargs = mock_client.works.create.call_args.kwargs
        assert call_kwargs["type"] == WorkType.TICKET

    async def test_create_with_priority_and_severity(self, mock_ctx, mock_client):
        """Test create with priority and severity."""
        work = _make_mock_work()
        mock_client.works.create.return_value = work

        await devrev_works_create(
            mock_ctx,
            title="Bug",
            applies_to_part="part1",
            type="issue",
            owned_by=["user1"],
            priority="p1",
            severity="high",
        )
        from devrev.models.works import IssuePriority, TicketSeverity

        call_kwargs = mock_client.works.create.call_args.kwargs
        assert call_kwargs["priority"] == IssuePriority.P1
        assert call_kwargs["severity"] == TicketSeverity.HIGH

    async def test_create_validation_error(self, mock_ctx, mock_client):
        """Test create raises RuntimeError on validation error."""
        from devrev.exceptions import ValidationError

        mock_client.works.create.side_effect = ValidationError("missing title")

        with pytest.raises(RuntimeError, match="Validation error"):
            await devrev_works_create(
                mock_ctx, title="", applies_to_part="p", type="ticket", owned_by=["u"]
            )


class TestWorksUpdateTool:
    """Tests for devrev_works_update tool."""

    async def test_update_title(self, mock_ctx, mock_client):
        """Test update work title."""
        work = _make_mock_work({"id": "w1", "title": "Updated"})
        mock_client.works.update.return_value = work

        result = await devrev_works_update(mock_ctx, id="w1", title="Updated")
        assert result["title"] == "Updated"
        mock_client.works.update.assert_called_once()

    async def test_update_with_priority(self, mock_ctx, mock_client):
        """Test update work with priority."""
        work = _make_mock_work()
        mock_client.works.update.return_value = work

        await devrev_works_update(mock_ctx, id="w1", priority="p0")
        from devrev.models.works import IssuePriority

        call_kwargs = mock_client.works.update.call_args.kwargs
        assert call_kwargs["priority"] == IssuePriority.P0


class TestWorksDeleteTool:
    """Tests for devrev_works_delete tool."""

    async def test_delete_returns_confirmation(self, mock_ctx, mock_client):
        """Test delete returns confirmation."""
        mock_client.works.delete.return_value = None

        result = await devrev_works_delete(mock_ctx, id="w1")
        assert result == {"deleted": True, "id": "w1"}

    async def test_delete_not_found(self, mock_ctx, mock_client):
        """Test delete raises RuntimeError when work not found."""
        from devrev.exceptions import NotFoundError

        mock_client.works.delete.side_effect = NotFoundError("not found")

        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_works_delete(mock_ctx, id="nonexistent")


class TestWorksCountTool:
    """Tests for devrev_works_count tool."""

    async def test_count_returns_integer(self, mock_ctx, mock_client):
        """Test count returns integer count."""
        mock_client.works.count.return_value = 42

        result = await devrev_works_count(mock_ctx)
        assert result == {"count": 42}

    async def test_count_with_type_filter(self, mock_ctx, mock_client):
        """Test count with work type filter."""
        mock_client.works.count.return_value = 5

        await devrev_works_count(mock_ctx, type=["ticket"])
        from devrev.models.works import WorkType

        call_kwargs = mock_client.works.count.call_args.kwargs
        assert call_kwargs["type"] == [WorkType.TICKET]


class TestWorksExportTool:
    """Tests for devrev_works_export tool."""

    async def test_export_returns_items(self, mock_ctx, mock_client):
        """Test export returns list of works."""
        work = _make_mock_work({"id": "w1"})
        mock_client.works.export.return_value = [work]

        result = await devrev_works_export(mock_ctx)
        assert result["count"] == 1
        assert len(result["works"]) == 1

    async def test_export_with_type_and_first(self, mock_ctx, mock_client):
        """Test export with type filter and limit."""
        mock_client.works.export.return_value = []

        await devrev_works_export(mock_ctx, type=["issue"], first=50)
        from devrev.models.works import WorkType

        call_kwargs = mock_client.works.export.call_args.kwargs
        assert call_kwargs["type"] == [WorkType.ISSUE]
        assert call_kwargs["first"] == 50


class TestWorksDocstringTerminology:
    """Verify all works tool docstrings clarify the ticket/issue/task terminology."""

    @pytest.mark.parametrize(
        "tool",
        [
            devrev_works_list,
            devrev_works_get,
            devrev_works_create,
            devrev_works_update,
            devrev_works_delete,
            devrev_works_count,
            devrev_works_export,
            devrev_works_list_modified_since,
            devrev_works_list_created_since,
        ],
    )
    def test_docstring_mentions_ticket_issue_task(self, tool):
        """Each works tool docstring must reference tickets, issues, and tasks."""
        doc = (tool.__doc__ or "").lower()
        assert "ticket" in doc, f"{tool.__name__} docstring missing 'ticket'"
        assert "issue" in doc, f"{tool.__name__} docstring missing 'issue'"
        assert "task" in doc, f"{tool.__name__} docstring missing 'task'"


class TestWorksListSortBy:
    """Tests for sort_by forwarding on devrev_works_list."""

    async def test_list_forwards_sort_by(self, mock_ctx, mock_client):
        """sort_by is forwarded unchanged to the SDK."""
        response = MagicMock()
        response.works = []
        response.next_cursor = None
        mock_client.works.list.return_value = response

        await devrev_works_list(mock_ctx, sort_by=["modified_date:desc", "-created_date"])
        call_kwargs = mock_client.works.list.call_args.kwargs
        assert call_kwargs["sort_by"] == ["modified_date:desc", "-created_date"]

    async def test_list_sort_by_defaults_to_none(self, mock_ctx, mock_client):
        """sort_by defaults to None and is forwarded as None."""
        response = MagicMock()
        response.works = []
        response.next_cursor = None
        mock_client.works.list.return_value = response

        await devrev_works_list(mock_ctx)
        call_kwargs = mock_client.works.list.call_args.kwargs
        assert call_kwargs["sort_by"] is None


class TestWorksExportSortBy:
    """Tests for sort_by forwarding on devrev_works_export."""

    async def test_export_forwards_sort_by(self, mock_ctx, mock_client):
        """sort_by is forwarded unchanged to the SDK."""
        mock_client.works.export.return_value = []

        await devrev_works_export(mock_ctx, sort_by=["created_date:asc"])
        call_kwargs = mock_client.works.export.call_args.kwargs
        assert call_kwargs["sort_by"] == ["created_date:asc"]

    async def test_export_sort_by_defaults_to_none(self, mock_ctx, mock_client):
        """sort_by defaults to None and is forwarded as None."""
        mock_client.works.export.return_value = []

        await devrev_works_export(mock_ctx)
        call_kwargs = mock_client.works.export.call_args.kwargs
        assert call_kwargs["sort_by"] is None


class TestWorksListModifiedSince:
    """Tests for devrev_works_list_modified_since tool."""

    async def test_parses_iso_with_z_suffix(self, mock_ctx, mock_client):
        """A trailing 'Z' is accepted and converted to a UTC datetime."""
        mock_client.works.list_modified_since.return_value = []

        await devrev_works_list_modified_since(mock_ctx, after="2024-01-15T12:34:56Z")
        args, _ = mock_client.works.list_modified_since.call_args
        assert args[0] == datetime(2024, 1, 15, 12, 34, 56, tzinfo=UTC)

    async def test_parses_iso_with_offset(self, mock_ctx, mock_client):
        """An explicit UTC offset is accepted."""
        mock_client.works.list_modified_since.return_value = []

        await devrev_works_list_modified_since(mock_ctx, after="2024-01-15T12:34:56+00:00")
        args, _ = mock_client.works.list_modified_since.call_args
        assert args[0] == datetime(2024, 1, 15, 12, 34, 56, tzinfo=UTC)

    async def test_invalid_iso_raises_runtime_error(self, mock_ctx, mock_client):
        """Invalid ISO input raises RuntimeError with a clear message."""
        with pytest.raises(RuntimeError, match="Invalid after format"):
            await devrev_works_list_modified_since(mock_ctx, after="not-a-date")
        mock_client.works.list_modified_since.assert_not_called()

    async def test_forwards_filter_kwargs(self, mock_ctx, mock_client):
        """type, owned_by, applies_to_part, and limit are forwarded."""
        mock_client.works.list_modified_since.return_value = []

        await devrev_works_list_modified_since(
            mock_ctx,
            after="2024-01-15T00:00:00Z",
            type=["ticket", "issue"],
            owned_by=["u1"],
            applies_to_part=["p1"],
            limit=500,
        )
        from devrev.models.works import WorkType

        call_kwargs = mock_client.works.list_modified_since.call_args.kwargs
        assert call_kwargs["type"] == [WorkType.TICKET, WorkType.ISSUE]
        assert call_kwargs["owned_by"] == ["u1"]
        assert call_kwargs["applies_to_part"] == ["p1"]
        assert call_kwargs["limit"] == 500

    async def test_returns_paginated_shape(self, mock_ctx, mock_client):
        """Returns a dict with count and works (no next_cursor)."""
        work = _make_mock_work({"id": "w1"})
        mock_client.works.list_modified_since.return_value = [work]

        result = await devrev_works_list_modified_since(mock_ctx, after="2024-01-15T00:00:00Z")
        assert result["count"] == 1
        assert result["works"][0]["id"] == "w1"
        assert "next_cursor" not in result


class TestWorksListCreatedSince:
    """Tests for devrev_works_list_created_since tool."""

    async def test_parses_iso_with_z_suffix(self, mock_ctx, mock_client):
        """A trailing 'Z' is accepted and converted to a UTC datetime."""
        mock_client.works.list_created_since.return_value = []

        await devrev_works_list_created_since(mock_ctx, after="2024-02-01T00:00:00Z")
        args, _ = mock_client.works.list_created_since.call_args
        assert args[0] == datetime(2024, 2, 1, 0, 0, 0, tzinfo=UTC)

    async def test_invalid_iso_raises_runtime_error(self, mock_ctx, mock_client):
        """Invalid ISO input raises RuntimeError with a clear message."""
        with pytest.raises(RuntimeError, match="Invalid after format"):
            await devrev_works_list_created_since(mock_ctx, after="bogus")
        mock_client.works.list_created_since.assert_not_called()

    async def test_forwards_filter_kwargs(self, mock_ctx, mock_client):
        """type, owned_by, applies_to_part, and limit are forwarded."""
        mock_client.works.list_created_since.return_value = []

        await devrev_works_list_created_since(
            mock_ctx,
            after="2024-02-01T00:00:00Z",
            type=["task"],
            owned_by=["u2"],
            applies_to_part=["p2"],
            limit=10,
        )
        from devrev.models.works import WorkType

        call_kwargs = mock_client.works.list_created_since.call_args.kwargs
        assert call_kwargs["type"] == [WorkType.TASK]
        assert call_kwargs["owned_by"] == ["u2"]
        assert call_kwargs["applies_to_part"] == ["p2"]
        assert call_kwargs["limit"] == 10

    async def test_returns_paginated_shape(self, mock_ctx, mock_client):
        """Returns a dict with count and works (no next_cursor)."""
        work = _make_mock_work({"id": "w9"})
        mock_client.works.list_created_since.return_value = [work]

        result = await devrev_works_list_created_since(mock_ctx, after="2024-02-01T00:00:00Z")
        assert result["count"] == 1
        assert result["works"][0]["id"] == "w9"
        assert "next_cursor" not in result
