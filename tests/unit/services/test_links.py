"""Unit tests for LinksService."""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.links import (
    Link,
    LinksCreateRequest,
    LinksDeleteRequest,
    LinksGetRequest,
    LinksListRequest,
    LinkType,
)
from devrev.services.links import LinksService

from .conftest import create_mock_response


class TestLinksService:
    """Tests for LinksService."""

    def test_create_link(
        self,
        mock_http_client: MagicMock,
        sample_link_data: dict[str, Any],
    ) -> None:
        """Test creating a link."""
        mock_http_client.post.return_value = create_mock_response(
            {"link": sample_link_data}
        )

        service = LinksService(mock_http_client)
        request = LinksCreateRequest(
            link_type=LinkType.IS_BLOCKED_BY,
            source="don:core:issue:456",
            target="don:core:issue:789",
        )
        result = service.create(request)

        assert isinstance(result, Link)
        assert result.id == "don:core:link:123"
        assert result.link_type == LinkType.IS_BLOCKED_BY
        mock_http_client.post.assert_called_once()

    def test_get_link(
        self,
        mock_http_client: MagicMock,
        sample_link_data: dict[str, Any],
    ) -> None:
        """Test getting a link by ID."""
        mock_http_client.post.return_value = create_mock_response(
            {"link": sample_link_data}
        )

        service = LinksService(mock_http_client)
        request = LinksGetRequest(id="don:core:link:123")
        result = service.get(request)

        assert isinstance(result, Link)
        assert result.id == "don:core:link:123"
        mock_http_client.post.assert_called_once()

    def test_list_links(
        self,
        mock_http_client: MagicMock,
        sample_link_data: dict[str, Any],
    ) -> None:
        """Test listing links."""
        mock_http_client.post.return_value = create_mock_response(
            {"links": [sample_link_data]}
        )

        service = LinksService(mock_http_client)
        result = service.list()

        assert len(result) == 1
        assert isinstance(result[0], Link)
        assert result[0].id == "don:core:link:123"
        mock_http_client.post.assert_called_once()

    def test_list_links_with_request(
        self,
        mock_http_client: MagicMock,
        sample_link_data: dict[str, Any],
    ) -> None:
        """Test listing links with pagination."""
        mock_http_client.post.return_value = create_mock_response(
            {"links": [sample_link_data]}
        )

        service = LinksService(mock_http_client)
        request = LinksListRequest(limit=50, cursor="next-cursor")
        result = service.list(request)

        assert len(result) == 1
        mock_http_client.post.assert_called_once()

    def test_list_links_by_object(
        self,
        mock_http_client: MagicMock,
        sample_link_data: dict[str, Any],
    ) -> None:
        """Test listing links filtered by object."""
        mock_http_client.post.return_value = create_mock_response(
            {"links": [sample_link_data]}
        )

        service = LinksService(mock_http_client)
        request = LinksListRequest(object="don:core:issue:456")
        result = service.list(request)

        assert len(result) == 1
        mock_http_client.post.assert_called_once()

    def test_delete_link(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test deleting a link."""
        mock_http_client.post.return_value = create_mock_response({})

        service = LinksService(mock_http_client)
        request = LinksDeleteRequest(id="don:core:link:123")
        result = service.delete(request)

        assert result is None
        mock_http_client.post.assert_called_once()

    def test_list_links_empty(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test listing links returns empty list."""
        mock_http_client.post.return_value = create_mock_response(
            {"links": []}
        )

        service = LinksService(mock_http_client)
        result = service.list()

        assert len(result) == 0
        mock_http_client.post.assert_called_once()

    def test_create_link_different_types(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test creating links with different link types."""
        link_data = {
            "id": "don:core:link:456",
            "source": "don:core:issue:100",
            "target": "don:core:issue:200",
            "link_type": "is_related_to",
        }
        mock_http_client.post.return_value = create_mock_response(
            {"link": link_data}
        )

        service = LinksService(mock_http_client)
        request = LinksCreateRequest(
            link_type=LinkType.IS_RELATED_TO,
            source="don:core:issue:100",
            target="don:core:issue:200",
        )
        result = service.create(request)

        assert result.link_type == LinkType.IS_RELATED_TO
        mock_http_client.post.assert_called_once()

