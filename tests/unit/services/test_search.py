"""Unit tests for SearchService."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from devrev.models.search import (
    CoreSearchRequest,
    HybridSearchRequest,
    SearchNamespace,
    SearchResponse,
)
from devrev.services.search import AsyncSearchService, SearchService

from .conftest import create_mock_response


class TestSearchRequestModels:
    """Regression tests for endpoint-specific namespace serialization."""

    @pytest.mark.parametrize("namespace", [SearchNamespace.ISSUE, SearchNamespace.PRODUCT])
    def test_hybrid_search_serializes_scalar_namespace(self, namespace: SearchNamespace) -> None:
        """Hybrid search sends one scalar namespace."""
        request = HybridSearchRequest(query="customer request", namespace=namespace)

        assert request.model_dump(mode="json") == {
            "query": "customer request",
            "namespace": namespace.value,
            "semantic_weight": None,
            "limit": None,
            "cursor": None,
        }

    def test_core_search_keeps_plural_namespaces(self) -> None:
        """Core search continues to send plural namespaces."""
        request = CoreSearchRequest(
            query="type:ticket",
            namespaces=[SearchNamespace.TICKET, SearchNamespace.ISSUE],
        )

        assert request.model_dump(mode="json")["namespaces"] == ["ticket", "issue"]
        assert "namespace" not in request.model_dump(mode="json")


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
        result = service.core("type:ticket AND priority:p0", namespace=SearchNamespace.WORK)

        assert isinstance(result, SearchResponse)
        assert len(result.results) == 2
        assert result.results[0].type == "work"
        assert result.results[0].work is not None
        assert result.results[0].work["id"] == "don:core:work:123"
        mock_http_client.post.assert_called_once_with(
            "/search.core",
            data={
                "query": "type:ticket AND priority:p0",
                "namespaces": ["work"],
            },
        )

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

    def test_core_search_with_namespace(
        self,
        mock_http_client: MagicMock,
        sample_search_response_data: dict[str, Any],
    ) -> None:
        """Test core search with namespace filtering."""
        mock_http_client.post.return_value = create_mock_response(sample_search_response_data)

        service = SearchService(mock_http_client)
        result = service.core(
            "authentication issues",
            namespace=SearchNamespace.ARTICLE,
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
        result = service.hybrid("login problems", namespace=SearchNamespace.ISSUE)

        assert isinstance(result, SearchResponse)
        assert len(result.results) == 2
        assert result.results[0].type == "work"
        mock_http_client.post.assert_called_once_with(
            "/search.hybrid",
            data={"query": "login problems", "namespace": "issue"},
        )

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
            namespace=SearchNamespace.CONVERSATION,
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
        empty_response: dict[str, Any] = {
            "results": [],
            "next_cursor": None,
            "total_count": 0,
        }
        mock_http_client.post.return_value = create_mock_response(empty_response)

        service = SearchService(mock_http_client)
        result = service.hybrid("nonexistent query", namespace=SearchNamespace.PRODUCT)

        assert isinstance(result, SearchResponse)
        assert len(result.results) == 0
        assert result.total_count == 0
        mock_http_client.post.assert_called_once_with(
            "/search.hybrid",
            data={"query": "nonexistent query", "namespace": "product"},
        )


class TestAsyncSearchService:
    """Tests for AsyncSearchService hybrid request construction."""

    @pytest.mark.asyncio
    async def test_hybrid_search_uses_scalar_issue_namespace(
        self,
        mock_async_http_client: AsyncMock,
        sample_search_response_data: dict[str, Any],
    ) -> None:
        """Async hybrid search sends a scalar issue namespace and returns results."""
        mock_async_http_client.post.return_value = create_mock_response(sample_search_response_data)

        service = AsyncSearchService(mock_async_http_client)
        result = await service.hybrid("login problems", namespace=SearchNamespace.ISSUE)

        assert len(result.results) == 2
        mock_async_http_client.post.assert_awaited_once_with(
            "/search.hybrid",
            data={"query": "login problems", "namespace": "issue"},
        )

    @pytest.mark.asyncio
    async def test_hybrid_search_returns_empty_product_results(
        self,
        mock_async_http_client: AsyncMock,
    ) -> None:
        """Async hybrid search accepts an empty product result set."""
        mock_async_http_client.post.return_value = create_mock_response(
            {"results": [], "total_count": 0}
        )

        service = AsyncSearchService(mock_async_http_client)
        result = await service.hybrid("unknown product", namespace=SearchNamespace.PRODUCT)

        assert result.results == []
        assert result.total_count == 0
        mock_async_http_client.post.assert_awaited_once_with(
            "/search.hybrid",
            data={"query": "unknown product", "namespace": "product"},
        )
