"""Unit tests for MCP search tools.

Tests for devrev_mcp.tools.search module covering hybrid and core search operations.
"""

from unittest.mock import MagicMock

import pytest

from devrev_mcp.tools.search import (
    _extract_display_name,
    _rerank_results,
    devrev_search_core,
    devrev_search_hybrid,
)


def _make_mock_search_result(data: dict | None = None) -> MagicMock:
    """Create a mock search result with realistic data format.

    Args:
        data: Optional dict to override default result data.

    Returns:
        MagicMock with model_dump method configured.
    """
    default = {
        "type": "work",
        "work": {"title": "Test work item", "display_id": "WORK-123"},
        "snippet": "A test result snippet",
    }
    result = MagicMock()
    result.model_dump.return_value = {**(data or default)}
    return result


class TestSearchHybridTool:
    """Tests for devrev_search_hybrid tool."""

    async def test_basic_search(self, mock_ctx, mock_client):
        """Test basic hybrid search without optional parameters."""
        sr = _make_mock_search_result()
        response = MagicMock()
        response.results = [sr]
        response.next_cursor = None
        response.total_count = 1
        mock_client.search.hybrid.return_value = response

        result = await devrev_search_hybrid(mock_ctx, query="test query", namespace="WORK")

        assert result["count"] == 1
        assert result["total_count"] == 1
        assert len(result["results"]) == 1
        mock_client.search.hybrid.assert_called_once()

    async def test_search_with_namespace(self, mock_ctx, mock_client):
        """Test hybrid search with namespace filtering."""
        response = MagicMock()
        response.results = []
        response.next_cursor = None
        response.total_count = 0
        mock_client.search.hybrid.return_value = response

        await devrev_search_hybrid(mock_ctx, query="q", namespace="WORK")

        from devrev.models.search import SearchNamespace

        call_kwargs = mock_client.search.hybrid.call_args
        assert call_kwargs.kwargs["namespace"] == SearchNamespace.WORK

    async def test_search_with_pagination(self, mock_ctx, mock_client):
        """Test hybrid search with pagination cursor."""
        response = MagicMock()
        response.results = []
        response.next_cursor = "next123"
        response.total_count = None
        mock_client.search.hybrid.return_value = response

        result = await devrev_search_hybrid(mock_ctx, query="q", namespace="WORK")

        assert result["next_cursor"] == "next123"
        assert "total_count" not in result  # None should not be included

    async def test_search_with_semantic_weight(self, mock_ctx, mock_client):
        """Test hybrid search with semantic weight parameter."""
        response = MagicMock()
        response.results = []
        response.next_cursor = None
        response.total_count = None
        mock_client.search.hybrid.return_value = response

        await devrev_search_hybrid(mock_ctx, query="q", namespace="WORK", semantic_weight=0.8)

        call_kwargs = mock_client.search.hybrid.call_args
        assert call_kwargs.kwargs["semantic_weight"] == 0.8

    async def test_search_error(self, mock_ctx, mock_client):
        """Test hybrid search error handling."""
        from devrev.exceptions import DevRevError

        mock_client.search.hybrid.side_effect = DevRevError("search failed")

        with pytest.raises(RuntimeError, match="API error"):
            await devrev_search_hybrid(mock_ctx, query="q", namespace="WORK")

    async def test_search_with_quoted_namespace(self, mock_ctx, mock_client):
        """Test hybrid search with quoted namespace input."""
        response = MagicMock()
        response.results = []
        response.next_cursor = None
        response.total_count = None
        mock_client.search.hybrid.return_value = response

        # Test with double quotes around namespace
        await devrev_search_hybrid(mock_ctx, query="q", namespace='"ACCOUNT"')

        from devrev.models.search import SearchNamespace

        call_kwargs = mock_client.search.hybrid.call_args
        assert call_kwargs.kwargs["namespace"] == SearchNamespace.ACCOUNT

    async def test_search_with_mixed_case_namespace(self, mock_ctx, mock_client):
        """Test hybrid search with mixed case namespace input."""
        response = MagicMock()
        response.results = []
        response.next_cursor = None
        response.total_count = None
        mock_client.search.hybrid.return_value = response

        # Test with mixed case
        await devrev_search_hybrid(mock_ctx, query="q", namespace="Account")

        from devrev.models.search import SearchNamespace

        call_kwargs = mock_client.search.hybrid.call_args
        assert call_kwargs.kwargs["namespace"] == SearchNamespace.ACCOUNT

    async def test_search_with_single_quoted_namespace(self, mock_ctx, mock_client):
        """Test hybrid search with single quoted namespace input."""
        response = MagicMock()
        response.results = []
        response.next_cursor = None
        response.total_count = None
        mock_client.search.hybrid.return_value = response

        # Test with single quotes
        await devrev_search_hybrid(mock_ctx, query="q", namespace="'work'")

        from devrev.models.search import SearchNamespace

        call_kwargs = mock_client.search.hybrid.call_args
        assert call_kwargs.kwargs["namespace"] == SearchNamespace.WORK

    async def test_search_with_whitespace_namespace(self, mock_ctx, mock_client):
        """Test hybrid search with whitespace around namespace."""
        response = MagicMock()
        response.results = []
        response.next_cursor = None
        response.total_count = None
        mock_client.search.hybrid.return_value = response

        # Test with whitespace
        await devrev_search_hybrid(mock_ctx, query="q", namespace="  ARTICLE  ")

        from devrev.models.search import SearchNamespace

        call_kwargs = mock_client.search.hybrid.call_args
        assert call_kwargs.kwargs["namespace"] == SearchNamespace.ARTICLE

    async def test_search_with_invalid_namespace(self, mock_ctx, mock_client):
        """Test hybrid search with invalid namespace."""
        response = MagicMock()
        response.results = []
        response.next_cursor = None
        response.total_count = None
        mock_client.search.hybrid.return_value = response

        # Test with invalid namespace
        with pytest.raises(RuntimeError, match="Invalid search namespace"):
            await devrev_search_hybrid(mock_ctx, query="q", namespace="INVALID")

    @pytest.mark.parametrize(
        "ns_str,ns_enum_name",
        [
            ("TICKET", "TICKET"),
            ("INCIDENT", "INCIDENT"),
            ("PRODUCT", "PRODUCT"),
            ("ENHANCEMENT", "ENHANCEMENT"),
            ("CUSTOM_WORK", "CUSTOM_WORK"),
        ],
    )
    async def test_search_hybrid_with_various_namespaces(
        self, mock_ctx, mock_client, ns_str, ns_enum_name
    ):
        """Test hybrid search with various namespace values."""
        mock_response = MagicMock()
        mock_response.results = [_make_mock_search_result()]
        mock_response.next_cursor = None
        mock_response.total_count = None
        mock_client.search.hybrid.return_value = mock_response

        result = await devrev_search_hybrid(mock_ctx, query="test", namespace=ns_str)

        assert "results" in result
        assert result["count"] == 1

        from devrev.models.search import SearchNamespace

        call_kwargs = mock_client.search.hybrid.call_args
        assert call_kwargs.kwargs["namespace"] == SearchNamespace[ns_enum_name]


class TestSearchCoreTool:
    """Tests for devrev_search_core tool."""

    async def test_basic_search(self, mock_ctx, mock_client):
        """Test basic core search without optional parameters."""
        sr = _make_mock_search_result()
        response = MagicMock()
        response.results = [sr]
        response.next_cursor = None
        response.total_count = 5
        mock_client.search.core.return_value = response

        result = await devrev_search_core(mock_ctx, query="test", namespace="WORK")

        assert result["count"] == 1
        assert result["total_count"] == 5
        mock_client.search.core.assert_called_once()

    async def test_core_search_with_namespace(self, mock_ctx, mock_client):
        """Test core search with namespace filtering."""
        response = MagicMock()
        response.results = []
        response.next_cursor = None
        response.total_count = None
        mock_client.search.core.return_value = response

        await devrev_search_core(mock_ctx, query="q", namespace="ARTICLE")

        from devrev.models.search import SearchNamespace

        call_kwargs = mock_client.search.core.call_args
        assert call_kwargs.kwargs["namespace"] == SearchNamespace.ARTICLE

    async def test_core_search_error(self, mock_ctx, mock_client):
        """Test core search error handling."""
        from devrev.exceptions import ServerError

        mock_client.search.core.side_effect = ServerError("internal error")

        with pytest.raises(RuntimeError, match="server error"):
            await devrev_search_core(mock_ctx, query="q", namespace="WORK")

    async def test_core_search_with_quoted_namespace(self, mock_ctx, mock_client):
        """Test core search with quoted namespace input."""
        response = MagicMock()
        response.results = []
        response.next_cursor = None
        response.total_count = None
        mock_client.search.core.return_value = response

        # Test with double quotes around namespace
        await devrev_search_core(mock_ctx, query="q", namespace='"CONVERSATION"')

        from devrev.models.search import SearchNamespace

        call_kwargs = mock_client.search.core.call_args
        assert call_kwargs.kwargs["namespace"] == SearchNamespace.CONVERSATION

    async def test_core_search_with_mixed_case_namespace(self, mock_ctx, mock_client):
        """Test core search with mixed case namespace input."""
        response = MagicMock()
        response.results = []
        response.next_cursor = None
        response.total_count = None
        mock_client.search.core.return_value = response

        # Test with mixed case
        await devrev_search_core(mock_ctx, query="q", namespace="Article")

        from devrev.models.search import SearchNamespace

        call_kwargs = mock_client.search.core.call_args
        assert call_kwargs.kwargs["namespace"] == SearchNamespace.ARTICLE

    async def test_core_search_does_not_rerank(self, mock_ctx, mock_client):
        """Core search should NOT apply client-side re-ranking."""
        # Create results where re-ranking would change order if applied
        sr1 = _make_mock_search_result(
            {"type": "account", "account": {"display_name": "Unrelated"}, "snippet": "..."}
        )
        sr2 = _make_mock_search_result(
            {"type": "account", "account": {"display_name": "MongoDB"}, "snippet": "..."}
        )
        response = MagicMock()
        response.results = [sr1, sr2]
        response.next_cursor = None
        response.total_count = None
        mock_client.search.core.return_value = response

        # Use "mongo" as query - if re-ranking were applied, MongoDB would move to position 0
        result = await devrev_search_core(mock_ctx, query="mongo", namespace="ACCOUNT")

        # Order should be preserved (no re-ranking)
        assert result["results"][0]["account"]["display_name"] == "Unrelated"
        assert result["results"][1]["account"]["display_name"] == "MongoDB"


class TestReranking:
    """Tests for client-side search result re-ranking."""

    def test_rerank_boosts_display_name_match(self):
        """Results with query substring in display_name should come first."""
        results = [
            {"type": "account", "account": {"display_name": "Acme Corp"}},
            {"type": "account", "account": {"display_name": "MongoDB Inc"}},
            {"type": "account", "account": {"display_name": "Other Company"}},
        ]
        reranked = _rerank_results(results, "mongo")
        assert reranked[0]["account"]["display_name"] == "MongoDB Inc"
        assert len(reranked) == 3

    def test_rerank_preserves_order_within_groups(self):
        """Relative order should be preserved within matched and unmatched groups."""
        results = [
            {"type": "account", "account": {"display_name": "Alpha"}},
            {"type": "account", "account": {"display_name": "MongoDB Atlas"}},
            {"type": "account", "account": {"display_name": "Beta"}},
            {"type": "account", "account": {"display_name": "MongoDB Cloud"}},
            {"type": "account", "account": {"display_name": "Gamma"}},
        ]
        reranked = _rerank_results(results, "mongo")
        # Matched group should be first, preserving relative order
        assert reranked[0]["account"]["display_name"] == "MongoDB Atlas"
        assert reranked[1]["account"]["display_name"] == "MongoDB Cloud"
        # Unmatched group follows, preserving relative order
        assert reranked[2]["account"]["display_name"] == "Alpha"
        assert reranked[3]["account"]["display_name"] == "Beta"
        assert reranked[4]["account"]["display_name"] == "Gamma"

    def test_rerank_case_insensitive(self):
        """Re-ranking should be case-insensitive."""
        results = [
            {"type": "account", "account": {"display_name": "Acme"}},
            {"type": "account", "account": {"display_name": "MONGODB"}},
        ]
        reranked = _rerank_results(results, "mongo")
        assert reranked[0]["account"]["display_name"] == "MONGODB"

    def test_rerank_no_match_preserves_original_order(self):
        """When no results match the query, original order should be preserved."""
        results = [
            {"type": "account", "account": {"display_name": "Alpha"}},
            {"type": "account", "account": {"display_name": "Beta"}},
            {"type": "account", "account": {"display_name": "Gamma"}},
        ]
        reranked = _rerank_results(results, "xyz")
        assert reranked == results

    def test_rerank_empty_results(self):
        """Empty results list should return empty."""
        assert _rerank_results([], "test") == []

    def test_rerank_empty_query(self):
        """Empty query should return results unchanged."""
        results = [{"type": "account", "account": {"display_name": "Test"}}]
        assert _rerank_results(results, "") == results

    def test_rerank_with_work_title(self):
        """Re-ranking should work with 'title' field on work items."""
        results = [
            {"type": "work", "work": {"title": "Unrelated ticket"}},
            {"type": "work", "work": {"title": "Fix MongoDB connection timeout"}},
        ]
        reranked = _rerank_results(results, "mongodb")
        assert reranked[0]["work"]["title"] == "Fix MongoDB connection timeout"

    def test_rerank_result_without_entity_dict(self):
        """Results without entity dicts should go to unmatched group."""
        results = [
            {"type": "unknown", "snippet": "some text"},
            {"type": "account", "account": {"display_name": "MongoDB"}},
        ]
        reranked = _rerank_results(results, "mongo")
        assert reranked[0]["account"]["display_name"] == "MongoDB"
        assert reranked[1]["type"] == "unknown"


class TestExtractDisplayName:
    """Tests for _extract_display_name helper."""

    def test_extract_from_account(self):
        result = {"type": "account", "account": {"display_name": "Acme Corp"}}
        assert _extract_display_name(result) == "Acme Corp"

    def test_extract_from_work_title(self):
        result = {"type": "work", "work": {"title": "Fix bug"}}
        assert _extract_display_name(result) == "Fix bug"

    def test_extract_returns_none_for_unknown(self):
        result = {"type": "unknown"}
        assert _extract_display_name(result) is None

    def test_extract_from_ticket(self):
        """Dynamic extraction should work for ticket type."""
        result = {"type": "ticket", "ticket": {"display_name": "Support Request"}}
        assert _extract_display_name(result) == "Support Request"

    def test_extract_from_incident(self):
        """Dynamic extraction should work for incident type."""
        result = {"type": "incident", "incident": {"title": "Service Outage"}}
        assert _extract_display_name(result) == "Service Outage"

    def test_extract_from_product(self):
        """Dynamic extraction should work for product type."""
        result = {"type": "product", "product": {"name": "Widget Pro"}}
        assert _extract_display_name(result) == "Widget Pro"

    def test_extract_from_custom_work(self):
        """Dynamic extraction should work for custom_work type."""
        result = {"type": "custom_work", "custom_work": {"title": "Custom Task"}}
        assert _extract_display_name(result) == "Custom Task"

    def test_extract_fallback_scans_all_dicts(self):
        """When type doesn't match entity key, fallback should scan all dict values."""
        result = {"type": "weird", "actual_data": {"display_name": "Found It"}}
        assert _extract_display_name(result) == "Found It"
