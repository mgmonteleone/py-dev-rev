"""Search service for DevRev SDK.

This module provides the SearchService for searching across DevRev objects.
"""

from __future__ import annotations

from typing import overload

from devrev.models.search import (
    CoreSearchRequest,
    HybridSearchRequest,
    SearchNamespace,
    SearchResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


class SearchService(BaseService):
    """Synchronous service for searching DevRev objects.

    Provides methods for core and hybrid search operations.
    """

    @overload
    def core(
        self,
        request_or_query: CoreSearchRequest,
        *,
        namespace: SearchNamespace | None = ...,
        limit: int | None = ...,
        cursor: str | None = ...,
    ) -> SearchResponse: ...

    @overload
    def core(
        self,
        request_or_query: str,
        *,
        namespace: SearchNamespace | None = ...,
        limit: int | None = ...,
        cursor: str | None = ...,
    ) -> SearchResponse: ...

    def core(
        self,
        request_or_query: CoreSearchRequest | str,
        *,
        namespace: SearchNamespace | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> SearchResponse:
        """Perform a core search with DevRev query language (beta only).

        Core search supports advanced query syntax for precise filtering.

        Args:
            request_or_query: Either a CoreSearchRequest object or a search query string.
            namespace: Object type to search in (e.g. WORK, ACCOUNT, ARTICLE).
                Required by the DevRev API when using keyword arguments.
            limit: Maximum number of results to return.
            cursor: Pagination cursor from previous response.

        Returns:
            SearchResponse with results, scores, and highlights.

        Example:
            >>> # Using keyword arguments
            >>> results = client.search.core(
            ...     query="type:ticket AND priority:p0",
            ...     namespace=SearchNamespace.WORK,
            ...     limit=20,
            ... )
            >>> for result in results.results:
            ...     print(f"{result.id}: {result.score}")
            >>>
            >>> # Using request object
            >>> request = CoreSearchRequest(
            ...     query="type:ticket AND status:open",
            ...     namespace=SearchNamespace.WORK,
            ... )
            >>> results = client.search.core(request)

        Note:
            This method is only available with beta API.
        """
        if isinstance(request_or_query, CoreSearchRequest):
            request = request_or_query
        else:
            if namespace is None:
                raise ValueError(
                    "namespace is required for search. "
                    "Provide a SearchNamespace value (e.g. SearchNamespace.WORK)."
                )
            request = CoreSearchRequest(
                query=request_or_query,
                namespace=namespace,
                limit=limit,
                cursor=cursor,
            )
        return self._post("/search.core", request, SearchResponse)

    @overload
    def hybrid(
        self,
        request_or_query: HybridSearchRequest,
        *,
        namespace: SearchNamespace | None = ...,
        semantic_weight: float | None = ...,
        limit: int | None = ...,
        cursor: str | None = ...,
    ) -> SearchResponse: ...

    @overload
    def hybrid(
        self,
        request_or_query: str,
        *,
        namespace: SearchNamespace | None = ...,
        semantic_weight: float | None = ...,
        limit: int | None = ...,
        cursor: str | None = ...,
    ) -> SearchResponse: ...

    def hybrid(
        self,
        request_or_query: HybridSearchRequest | str,
        *,
        namespace: SearchNamespace | None = None,
        semantic_weight: float | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> SearchResponse:
        """Perform a hybrid search combining keyword and semantic search.

        Hybrid search blends traditional keyword matching with semantic understanding
        for more intelligent results.

        Args:
            request_or_query: Either a HybridSearchRequest object or a search query string.
            namespace: Object type to search in (e.g. WORK, ACCOUNT, ARTICLE).
                Required by the DevRev API when using keyword arguments.
            semantic_weight: Weight for semantic search component (0-1).
                Higher values favor semantic matching over keyword matching.
            limit: Maximum number of results to return.
            cursor: Pagination cursor from previous response.

        Returns:
            SearchResponse with results, scores, and highlights.

        Example:
            >>> # Using keyword arguments
            >>> results = client.search.hybrid(
            ...     query="authentication issues",
            ...     namespace=SearchNamespace.CONVERSATION,
            ...     semantic_weight=0.7,
            ...     limit=10,
            ... )
            >>> for result in results.results:
            ...     print(f"{result.id}: {result.score}")
            >>>
            >>> # Using request object
            >>> request = HybridSearchRequest(
            ...     query="login problems",
            ...     namespace=SearchNamespace.WORK,
            ...     semantic_weight=0.5,
            ... )
            >>> results = client.search.hybrid(request)

        Note:
            This method is only available with beta API.
        """
        if isinstance(request_or_query, HybridSearchRequest):
            request = request_or_query
        else:
            if namespace is None:
                raise ValueError(
                    "namespace is required for search. "
                    "Provide a SearchNamespace value (e.g. SearchNamespace.WORK)."
                )
            request = HybridSearchRequest(
                query=request_or_query,
                namespace=namespace,
                semantic_weight=semantic_weight,
                limit=limit,
                cursor=cursor,
            )
        return self._post("/search.hybrid", request, SearchResponse)


class AsyncSearchService(AsyncBaseService):
    """Asynchronous service for searching DevRev objects.

    Provides async methods for core and hybrid search operations.
    """

    @overload
    async def core(
        self,
        request_or_query: CoreSearchRequest,
        *,
        namespace: SearchNamespace | None = ...,
        limit: int | None = ...,
        cursor: str | None = ...,
    ) -> SearchResponse: ...

    @overload
    async def core(
        self,
        request_or_query: str,
        *,
        namespace: SearchNamespace | None = ...,
        limit: int | None = ...,
        cursor: str | None = ...,
    ) -> SearchResponse: ...

    async def core(
        self,
        request_or_query: CoreSearchRequest | str,
        *,
        namespace: SearchNamespace | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> SearchResponse:
        """Perform a core search with DevRev query language (beta only).

        Core search supports advanced query syntax for precise filtering.

        Args:
            request_or_query: Either a CoreSearchRequest object or a search query string.
            namespace: Object type to search in (e.g. WORK, ACCOUNT, ARTICLE).
                Required by the DevRev API when using keyword arguments.
            limit: Maximum number of results to return.
            cursor: Pagination cursor from previous response.

        Returns:
            SearchResponse with results, scores, and highlights.

        Example:
            >>> # Using keyword arguments
            >>> results = await client.search.core(
            ...     query="type:ticket AND priority:p0",
            ...     namespace=SearchNamespace.WORK,
            ...     limit=20,
            ... )
            >>> for result in results.results:
            ...     print(f"{result.id}: {result.score}")
            >>>
            >>> # Using request object
            >>> request = CoreSearchRequest(
            ...     query="type:ticket AND status:open",
            ...     namespace=SearchNamespace.WORK,
            ... )
            >>> results = await client.search.core(request)

        Note:
            This method is only available with beta API.
        """
        if isinstance(request_or_query, CoreSearchRequest):
            request = request_or_query
        else:
            if namespace is None:
                raise ValueError(
                    "namespace is required for search. "
                    "Provide a SearchNamespace value (e.g. SearchNamespace.WORK)."
                )
            request = CoreSearchRequest(
                query=request_or_query,
                namespace=namespace,
                limit=limit,
                cursor=cursor,
            )
        return await self._post("/search.core", request, SearchResponse)

    @overload
    async def hybrid(
        self,
        request_or_query: HybridSearchRequest,
        *,
        namespace: SearchNamespace | None = ...,
        semantic_weight: float | None = ...,
        limit: int | None = ...,
        cursor: str | None = ...,
    ) -> SearchResponse: ...

    @overload
    async def hybrid(
        self,
        request_or_query: str,
        *,
        namespace: SearchNamespace | None = ...,
        semantic_weight: float | None = ...,
        limit: int | None = ...,
        cursor: str | None = ...,
    ) -> SearchResponse: ...

    async def hybrid(
        self,
        request_or_query: HybridSearchRequest | str,
        *,
        namespace: SearchNamespace | None = None,
        semantic_weight: float | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> SearchResponse:
        """Perform a hybrid search combining keyword and semantic search.

        Hybrid search blends traditional keyword matching with semantic understanding
        for more intelligent results.

        Args:
            request_or_query: Either a HybridSearchRequest object or a search query string.
            namespace: Object type to search in (e.g. WORK, ACCOUNT, ARTICLE).
                Required by the DevRev API when using keyword arguments.
            semantic_weight: Weight for semantic search component (0-1).
                Higher values favor semantic matching over keyword matching.
            limit: Maximum number of results to return.
            cursor: Pagination cursor from previous response.

        Returns:
            SearchResponse with results, scores, and highlights.

        Example:
            >>> # Using keyword arguments
            >>> results = await client.search.hybrid(
            ...     query="authentication issues",
            ...     namespace=SearchNamespace.CONVERSATION,
            ...     semantic_weight=0.7,
            ...     limit=10,
            ... )
            >>> for result in results.results:
            ...     print(f"{result.id}: {result.score}")
            >>>
            >>> # Using request object
            >>> request = HybridSearchRequest(
            ...     query="login problems",
            ...     namespace=SearchNamespace.WORK,
            ...     semantic_weight=0.5,
            ... )
            >>> results = await client.search.hybrid(request)

        Note:
            This method is only available with beta API.
        """
        if isinstance(request_or_query, HybridSearchRequest):
            request = request_or_query
        else:
            if namespace is None:
                raise ValueError(
                    "namespace is required for search. "
                    "Provide a SearchNamespace value (e.g. SearchNamespace.WORK)."
                )
            request = HybridSearchRequest(
                query=request_or_query,
                namespace=namespace,
                semantic_weight=semantic_weight,
                limit=limit,
                cursor=cursor,
            )
        return await self._post("/search.hybrid", request, SearchResponse)
