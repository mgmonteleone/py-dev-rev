"""Unit tests for DevRev MCP link tools."""

from __future__ import annotations

from inspect import getdoc
from typing import Any
from unittest.mock import MagicMock

import pytest

from devrev.exceptions import NotFoundError, ValidationError
from devrev_mcp.tools.links import (
    devrev_links_create,
    devrev_links_delete,
    devrev_links_get,
    devrev_links_list,
)


def _make_mock_link(data: dict[str, Any] | None = None) -> MagicMock:
    """Create a mock Link model with model_dump method.

    Args:
        data: Optional dict to return from model_dump.

    Returns:
        MagicMock with model_dump method.
    """
    mock = MagicMock()
    default_data = {
        "id": "don:core:dvrv-us-1:devo/1:link/123",
        "link_type": "is_related_to",
        "source": "don:core:dvrv-us-1:devo/1:ticket/1",
        "target": "don:core:dvrv-us-1:devo/1:ticket/2",
        "created_date": "2026-01-01T00:00:00Z",
    }
    if data:
        default_data.update(data)
    mock.model_dump.return_value = default_data
    return mock


class TestLinksListTool:
    """Tests for devrev_links_list tool."""

    async def test_list_empty(self, mock_ctx, mock_client):
        """Test listing links with empty results."""
        # Arrange
        mock_client.links.list.return_value = []

        # Act
        result = await devrev_links_list(mock_ctx)

        # Assert
        assert result["count"] == 0
        assert result["links"] == []
        mock_client.links.list.assert_called_once()

    async def test_list_success(self, mock_ctx, mock_client):
        """Test listing links with results."""
        # Arrange
        link1 = _make_mock_link({"id": "link-1", "link_type": "is_related_to"})
        link2 = _make_mock_link({"id": "link-2", "link_type": "is_blocked_by"})
        mock_client.links.list.return_value = [link1, link2]

        # Act
        result = await devrev_links_list(mock_ctx)

        # Assert
        assert result["count"] == 2
        assert len(result["links"]) == 2
        assert result["links"][0]["id"] == "link-1"
        assert result["links"][1]["id"] == "link-2"

    async def test_list_with_object_filter(self, mock_ctx, mock_client):
        """Test listing links filtered by object ID."""
        # Arrange
        link = _make_mock_link()
        mock_client.links.list.return_value = [link]

        # Act
        result = await devrev_links_list(mock_ctx, object_id="don:core:dvrv-us-1:devo/1:ticket/123")

        # Assert
        assert result["count"] == 1
        mock_client.links.list.assert_called_once()

    async def test_list_with_pagination(self, mock_ctx, mock_client):
        """Test listing links with pagination parameters."""
        # Arrange
        link = _make_mock_link()
        mock_client.links.list.return_value = [link]

        # Act
        result = await devrev_links_list(mock_ctx, cursor="cursor-123", limit=10)

        # Assert
        assert result["count"] == 1
        mock_client.links.list.assert_called_once()

    async def test_list_error(self, mock_ctx, mock_client):
        """Test listing links with error."""
        # Arrange
        mock_client.links.list.side_effect = NotFoundError("Not found", status_code=404)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_links_list(mock_ctx)


class TestLinksGetTool:
    """Tests for devrev_links_get tool."""

    async def test_get_success(self, mock_ctx, mock_client):
        """Test getting a link successfully."""
        # Arrange
        link = _make_mock_link()
        mock_client.links.get.return_value = link

        # Act
        result = await devrev_links_get(mock_ctx, id="link-123")

        # Assert
        assert result["id"] == "don:core:dvrv-us-1:devo/1:link/123"
        assert result["link_type"] == "is_related_to"
        mock_client.links.get.assert_called_once()

    async def test_get_error(self, mock_ctx, mock_client):
        """Test getting a non-existent link."""
        # Arrange
        mock_client.links.get.side_effect = NotFoundError("Link not found", status_code=404)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Link not found"):
            await devrev_links_get(mock_ctx, id="link-999")


class TestLinksCreateTool:
    """Tests for devrev_links_create tool."""

    async def test_create_success(self, mock_ctx, mock_client):
        """Test creating a link successfully."""
        # Arrange
        link = _make_mock_link()
        mock_client.links.create.return_value = link

        # Act
        result = await devrev_links_create(
            mock_ctx,
            link_type="is_related_to",
            source="don:core:dvrv-us-1:devo/1:ticket/1",
            target="don:core:dvrv-us-1:devo/1:ticket/2",
        )

        # Assert
        assert result["id"] == "don:core:dvrv-us-1:devo/1:link/123"
        assert result["link_type"] == "is_related_to"
        mock_client.links.create.assert_called_once()

    async def test_create_ticket_dependency_forwards_link_type(self, mock_ctx, mock_client):
        """Test forwarding is_dependent_on for a ticket-to-issue link."""
        link = _make_mock_link({"link_type": "is_dependent_on"})
        mock_client.links.create.return_value = link

        result = await devrev_links_create(
            mock_ctx,
            link_type="is_dependent_on",
            source="don:core:dvrv-us-1:devo/1:ticket/1",
            target="don:core:dvrv-us-1:devo/1:issue/2",
        )

        assert result["link_type"] == "is_dependent_on"
        request = mock_client.links.create.call_args.args[0]
        assert request.link_type == "is_dependent_on"
        assert request.source.endswith(":ticket/1")
        assert request.target.endswith(":issue/2")

    async def test_create_with_custom_type(self, mock_ctx, mock_client):
        """Test creating a link with custom link type."""
        # Arrange
        link = _make_mock_link({"link_type": "custom_link_type"})
        mock_client.links.create.return_value = link

        # Act
        result = await devrev_links_create(
            mock_ctx,
            link_type="custom_link_type",
            source="don:core:dvrv-us-1:devo/1:ticket/1",
            target="don:core:dvrv-us-1:devo/1:ticket/2",
        )

        # Assert
        assert result["link_type"] == "custom_link_type"
        mock_client.links.create.assert_called_once()

    def test_create_docs_list_valid_link_types(self):
        """Test link guidance contains the accepted values and reported association."""
        docs = getdoc(devrev_links_create)
        assert docs is not None
        for link_type in (
            "custom_link",
            "developed_with",
            "imports",
            "is_analyzed_by",
            "is_converted_to",
            "is_dependent_on",
            "is_duplicate_of",
            "is_follow_up_of",
            "is_merged_into",
            "is_parent_of",
            "is_part_of",
            "is_related_to",
            "serves",
        ):
            assert link_type in docs
        assert "is_blocked_by" not in docs
        assert "ticket" in docs
        assert "tracking issue" in docs

    def test_create_docs_flag_custom_link_as_unsupported(self):
        """Test link guidance distinguishes the API enum from tool support.

        custom_link is a valid DevRev link-type enum value, but creating one
        also requires a custom_link_type ID that this tool does not accept.
        The docstring must say so explicitly rather than implying custom_link
        works like the other built-in values.
        """
        docs = getdoc(devrev_links_create)
        assert docs is not None
        normalized = " ".join(docs.split())
        assert "custom_link_type" in normalized
        assert "does not accept" in normalized
        # The unsupported caveat must be attached to custom_link, not floating
        # generic text elsewhere in the docstring.
        custom_link_index = normalized.index("custom_link")
        unsupported_index = normalized.index("except custom_link")
        assert unsupported_index >= custom_link_index

    async def test_create_validation_error_includes_response_detail(self, mock_ctx, mock_client):
        """Test creating a link surfaces DevRev's response detail."""
        mock_client.links.create.side_effect = ValidationError(
            "Bad Request",
            status_code=400,
            response_body={"detail": "link_type is not valid for this source and target"},
        )

        with pytest.raises(RuntimeError, match="link_type is not valid"):
            await devrev_links_create(
                mock_ctx,
                link_type="is_related_to",
                source="don:core:dvrv-us-1:devo/1:ticket/1",
                target="don:core:dvrv-us-1:devo/1:issue/2",
            )

    async def test_create_validation_error_without_detail_uses_fallback(
        self, mock_ctx, mock_client
    ):
        """Test creating a link preserves existing formatting without detail."""
        mock_client.links.create.side_effect = ValidationError(
            "Bad Request", status_code=400, response_body={"request_id": "request-1"}
        )

        with pytest.raises(RuntimeError, match=r"^Validation error: Bad Request\.$"):
            await devrev_links_create(
                mock_ctx,
                link_type="is_related_to",
                source="don:core:dvrv-us-1:devo/1:ticket/1",
                target="don:core:dvrv-us-1:devo/1:issue/2",
            )

    async def test_create_validation_error_with_none_response_body_uses_fallback(
        self, mock_ctx, mock_client
    ):
        """Test creating a link with no response body at all falls back safely."""
        mock_client.links.create.side_effect = ValidationError(
            "Bad Request", status_code=400, response_body=None
        )

        with pytest.raises(RuntimeError, match=r"^Validation error: Bad Request\.$"):
            await devrev_links_create(
                mock_ctx,
                link_type="is_related_to",
                source="don:core:dvrv-us-1:devo/1:ticket/1",
                target="don:core:dvrv-us-1:devo/1:issue/2",
            )

    @pytest.mark.parametrize("detail", ["", "   "])
    async def test_create_validation_error_with_empty_detail_uses_fallback(
        self, mock_ctx, mock_client, detail
    ):
        """Test an empty or whitespace-only detail does not get appended."""
        mock_client.links.create.side_effect = ValidationError(
            "Bad Request", status_code=400, response_body={"detail": detail}
        )

        with pytest.raises(RuntimeError, match=r"^Validation error: Bad Request\.$"):
            await devrev_links_create(
                mock_ctx,
                link_type="is_related_to",
                source="don:core:dvrv-us-1:devo/1:ticket/1",
                target="don:core:dvrv-us-1:devo/1:issue/2",
            )

    async def test_create_validation_error_with_non_string_detail_uses_fallback(
        self, mock_ctx, mock_client
    ):
        """Test a non-string detail value does not crash and is not appended."""
        mock_client.links.create.side_effect = ValidationError(
            "Bad Request",
            status_code=400,
            response_body={"detail": {"code": "invalid_link_type"}},
        )

        with pytest.raises(RuntimeError, match=r"^Validation error: Bad Request\.$"):
            await devrev_links_create(
                mock_ctx,
                link_type="is_related_to",
                source="don:core:dvrv-us-1:devo/1:ticket/1",
                target="don:core:dvrv-us-1:devo/1:issue/2",
            )

    async def test_create_not_found_error_skips_detail_extraction(self, mock_ctx, mock_client):
        """Test non-ValidationError DevRevErrors bypass the detail-extraction branch."""
        mock_client.links.create.side_effect = NotFoundError(
            "Object not found",
            status_code=404,
            response_body={"detail": "should not be surfaced by the ValidationError path"},
        )

        with pytest.raises(RuntimeError, match=r"^Not found: Object not found$") as excinfo:
            await devrev_links_create(
                mock_ctx,
                link_type="is_related_to",
                source="don:core:dvrv-us-1:devo/1:ticket/1",
                target="don:core:dvrv-us-1:devo/1:issue/2",
            )
        assert "Detail:" not in str(excinfo.value)


class TestLinksDeleteTool:
    """Tests for devrev_links_delete tool."""

    async def test_delete_success(self, mock_ctx, mock_client):
        """Test deleting a link successfully."""
        # Arrange
        mock_client.links.delete.return_value = None

        # Act
        result = await devrev_links_delete(mock_ctx, id="link-123")

        # Assert
        assert result["deleted"] is True
        assert result["id"] == "link-123"
        mock_client.links.delete.assert_called_once()

    async def test_delete_not_found(self, mock_ctx, mock_client):
        """Test deleting a non-existent link."""
        # Arrange
        mock_client.links.delete.side_effect = NotFoundError("Link not found", status_code=404)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Link not found"):
            await devrev_links_delete(mock_ctx, id="link-999")
