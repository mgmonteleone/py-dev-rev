"""Search service for DevRev SDK.

This module provides the SearchService for searching across DevRev objects.
"""

from __future__ import annotations

from devrev.models.search import (
    CoreSearchRequest,
    HybridSearchRequest,
    SearchResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


class SearchService(BaseService):
    """Synchronous service for searching DevRev objects.

    Provides methods for core and hybrid search operations.
    """

    def core(self, request: CoreSearchRequest) -> SearchResponse:
        """Perform a core search.

        Args:
            request: Core search request

        Returns:
            Search results
        """
        return self._post("/search.core", request, SearchResponse)

    def hybrid(self, request: HybridSearchRequest) -> SearchResponse:
        """Perform a hybrid search combining keyword and semantic search.

        Args:
            request: Hybrid search request

        Returns:
            Search results
        """
        return self._post("/search.hybrid", request, SearchResponse)


class AsyncSearchService(AsyncBaseService):
    """Asynchronous service for searching DevRev objects.

    Provides async methods for core and hybrid search operations.
    """

    async def core(self, request: CoreSearchRequest) -> SearchResponse:
        """Perform a core search."""
        return await self._post("/search.core", request, SearchResponse)

    async def hybrid(self, request: HybridSearchRequest) -> SearchResponse:
        """Perform a hybrid search combining keyword and semantic search."""
        return await self._post("/search.hybrid", request, SearchResponse)
