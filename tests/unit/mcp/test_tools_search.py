"""Unit tests for MCP search tools.

Tests for devrev_mcp.tools.search module covering hybrid and core search operations.
"""

from unittest.mock import MagicMock

import pytest

from devrev_mcp.tools.search import devrev_search_core, devrev_search_hybrid


def _make_mock_search_result(data: dict | None = None) -> MagicMock:
    """Create a mock search result with model_dump method.

    Args:
        data: Optional dict to override default result data.

    Returns:
        MagicMock with model_dump method configured.
    """
    default = {"id": "result-1", "type": "work", "score": 0.95}
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

        result = await devrev_search_hybrid(mock_ctx, query="test query")

        assert result["count"] == 1
        assert result["total_count"] == 1
        assert len(result["results"]) == 1
        mock_client.search.hybrid.assert_called_once()

    async def test_search_with_namespaces(self, mock_ctx, mock_client):
        """Test hybrid search with namespace filtering."""
        response = MagicMock()
        response.results = []
        response.next_cursor = None
        response.total_count = 0
        mock_client.search.hybrid.return_value = response

        await devrev_search_hybrid(mock_ctx, query="q", namespaces=["WORK", "ACCOUNT"])

        from devrev.models.search import SearchNamespace

        call_kwargs = mock_client.search.hybrid.call_args
        assert call_kwargs.kwargs["namespaces"] == [SearchNamespace.WORK, SearchNamespace.ACCOUNT]

    async def test_search_with_pagination(self, mock_ctx, mock_client):
        """Test hybrid search with pagination cursor."""
        response = MagicMock()
        response.results = []
        response.next_cursor = "next123"
        response.total_count = None
        mock_client.search.hybrid.return_value = response

        result = await devrev_search_hybrid(mock_ctx, query="q")

        assert result["next_cursor"] == "next123"
        assert "total_count" not in result  # None should not be included

    async def test_search_with_semantic_weight(self, mock_ctx, mock_client):
        """Test hybrid search with semantic weight parameter."""
        response = MagicMock()
        response.results = []
        response.next_cursor = None
        response.total_count = None
        mock_client.search.hybrid.return_value = response

        await devrev_search_hybrid(mock_ctx, query="q", semantic_weight=0.8)

        call_kwargs = mock_client.search.hybrid.call_args
        assert call_kwargs.kwargs["semantic_weight"] == 0.8

    async def test_search_error(self, mock_ctx, mock_client):
        """Test hybrid search error handling."""
        from devrev.exceptions import DevRevError

        mock_client.search.hybrid.side_effect = DevRevError("search failed")

        with pytest.raises(RuntimeError, match="API error"):
            await devrev_search_hybrid(mock_ctx, query="q")


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

        result = await devrev_search_core(mock_ctx, query="test")

        assert result["count"] == 1
        assert result["total_count"] == 5
        mock_client.search.core.assert_called_once()

    async def test_core_search_with_namespaces(self, mock_ctx, mock_client):
        """Test core search with namespace filtering."""
        response = MagicMock()
        response.results = []
        response.next_cursor = None
        response.total_count = None
        mock_client.search.core.return_value = response

        await devrev_search_core(mock_ctx, query="q", namespaces=["ARTICLE"])

        from devrev.models.search import SearchNamespace

        call_kwargs = mock_client.search.core.call_args
        assert call_kwargs.kwargs["namespaces"] == [SearchNamespace.ARTICLE]

    async def test_core_search_error(self, mock_ctx, mock_client):
        """Test core search error handling."""
        from devrev.exceptions import ServerError

        mock_client.search.core.side_effect = ServerError("internal error")

        with pytest.raises(RuntimeError, match="server error"):
            await devrev_search_core(mock_ctx, query="q")
