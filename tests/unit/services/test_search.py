"""Unit tests for SearchService."""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.search import (
    CoreSearchRequest,
    HybridSearchRequest,
    SearchNamespace,
    SearchResponse,
)
from devrev.services.search import SearchService

from .conftest import create_mock_response


class TestSearchService:
    """Tests for SearchService."""

    def test_core_search_with_string_query(
        self,
        mock_http_client: MagicMock,
        sample_search_response_data: dict[str, Any],
    ) -> None:
        """Test core search with a string query."""
        mock_http_client.post.return_value = create_mock_response(sample_search_response_data)

        service = SearchService(mock_http_client)
        result = service.core("type:ticket AND priority:p0")

        assert isinstance(result, SearchResponse)
        assert len(result.results) == 2
        assert result.results[0].id == "don:core:work:123"
        assert result.results[0].score == 0.95
        mock_http_client.post.assert_called_once()

    def test_core_search_with_request_object(
        self,
        mock_http_client: MagicMock,
        sample_search_response_data: dict[str, Any],
    ) -> None:
        """Test core search with a CoreSearchRequest object."""
        mock_http_client.post.return_value = create_mock_response(sample_search_response_data)

        service = SearchService(mock_http_client)
        request = CoreSearchRequest(
            query="type:ticket AND status:open",
            namespaces=[SearchNamespace.WORK],
            limit=20,
        )
        result = service.core(request)

        assert isinstance(result, SearchResponse)
        assert len(result.results) == 2
        mock_http_client.post.assert_called_once()

    def test_core_search_with_namespaces(
        self,
        mock_http_client: MagicMock,
        sample_search_response_data: dict[str, Any],
    ) -> None:
        """Test core search with namespace filtering."""
        mock_http_client.post.return_value = create_mock_response(sample_search_response_data)

        service = SearchService(mock_http_client)
        result = service.core(
            "authentication issues",
            namespaces=[SearchNamespace.ARTICLE, SearchNamespace.CONVERSATION],
            limit=10,
        )

        assert isinstance(result, SearchResponse)
        assert len(result.results) == 2
        mock_http_client.post.assert_called_once()

    def test_hybrid_search(
        self,
        mock_http_client: MagicMock,
        sample_search_response_data: dict[str, Any],
    ) -> None:
        """Test hybrid search with default parameters."""
        mock_http_client.post.return_value = create_mock_response(sample_search_response_data)

        service = SearchService(mock_http_client)
        result = service.hybrid("login problems")

        assert isinstance(result, SearchResponse)
        assert len(result.results) == 2
        assert result.results[0].type == "work"
        mock_http_client.post.assert_called_once()

    def test_hybrid_search_with_semantic_weight(
        self,
        mock_http_client: MagicMock,
        sample_search_response_data: dict[str, Any],
    ) -> None:
        """Test hybrid search with custom semantic weight."""
        mock_http_client.post.return_value = create_mock_response(sample_search_response_data)

        service = SearchService(mock_http_client)
        request = HybridSearchRequest(
            query="authentication issues",
            namespaces=[SearchNamespace.CONVERSATION, SearchNamespace.ARTICLE],
            semantic_weight=0.7,
            limit=10,
        )
        result = service.hybrid(request)

        assert isinstance(result, SearchResponse)
        assert len(result.results) == 2
        mock_http_client.post.assert_called_once()

    def test_search_empty_results(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test search returns empty results."""
        empty_response = {
            "results": [],
            "next_cursor": None,
            "total_count": 0,
        }
        mock_http_client.post.return_value = create_mock_response(empty_response)

        service = SearchService(mock_http_client)
        result = service.core("nonexistent query")

        assert isinstance(result, SearchResponse)
        assert len(result.results) == 0
        assert result.total_count == 0
        mock_http_client.post.assert_called_once()
