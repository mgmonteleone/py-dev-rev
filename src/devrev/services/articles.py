"""Articles service for DevRev SDK."""

from __future__ import annotations

from collections.abc import Sequence

from devrev.models.articles import (
    Article,
    ArticlesCountRequest,
    ArticlesCountResponse,
    ArticlesCreateRequest,
    ArticlesCreateResponse,
    ArticlesDeleteRequest,
    ArticlesDeleteResponse,
    ArticlesGetRequest,
    ArticlesGetResponse,
    ArticlesListRequest,
    ArticlesListResponse,
    ArticlesUpdateRequest,
    ArticlesUpdateResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


class ArticlesService(BaseService):
    """Service for managing DevRev Articles."""

    def create(self, request: ArticlesCreateRequest) -> Article:
        """Create a new article."""
        response = self._post("/articles.create", request, ArticlesCreateResponse)
        return response.article

    def get(self, request: ArticlesGetRequest) -> Article:
        """Get an article by ID."""
        response = self._post("/articles.get", request, ArticlesGetResponse)
        return response.article

    def list(self, request: ArticlesListRequest | None = None) -> Sequence[Article]:
        """List articles."""
        if request is None:
            request = ArticlesListRequest()
        response = self._post("/articles.list", request, ArticlesListResponse)
        return response.articles

    def update(self, request: ArticlesUpdateRequest) -> Article:
        """Update an article."""
        response = self._post("/articles.update", request, ArticlesUpdateResponse)
        return response.article

    def delete(self, request: ArticlesDeleteRequest) -> None:
        """Delete an article."""
        self._post("/articles.delete", request, ArticlesDeleteResponse)

    def count(
        self,
        *,
        status: list[str] | None = None,
    ) -> int:
        """Count articles (beta only).

        Args:
            status: Filter by article status

        Returns:
            Count of matching articles

        Raises:
            BetaAPIRequiredError: If not using beta API
        """
        request = ArticlesCountRequest(status=status)
        response = self._post("/articles.count", request, ArticlesCountResponse)
        return response.count


class AsyncArticlesService(AsyncBaseService):
    """Async service for managing DevRev Articles."""

    async def create(self, request: ArticlesCreateRequest) -> Article:
        """Create a new article."""
        response = await self._post("/articles.create", request, ArticlesCreateResponse)
        return response.article

    async def get(self, request: ArticlesGetRequest) -> Article:
        """Get an article by ID."""
        response = await self._post("/articles.get", request, ArticlesGetResponse)
        return response.article

    async def list(self, request: ArticlesListRequest | None = None) -> Sequence[Article]:
        """List articles."""
        if request is None:
            request = ArticlesListRequest()
        response = await self._post("/articles.list", request, ArticlesListResponse)
        return response.articles

    async def update(self, request: ArticlesUpdateRequest) -> Article:
        """Update an article."""
        response = await self._post("/articles.update", request, ArticlesUpdateResponse)
        return response.article

    async def delete(self, request: ArticlesDeleteRequest) -> None:
        """Delete an article."""
        await self._post("/articles.delete", request, ArticlesDeleteResponse)

    async def count(
        self,
        *,
        status: list[str] | None = None,
    ) -> int:
        """Count articles (beta only).

        Args:
            status: Filter by article status

        Returns:
            Count of matching articles

        Raises:
            BetaAPIRequiredError: If not using beta API
        """
        request = ArticlesCountRequest(status=status)
        response = await self._post("/articles.count", request, ArticlesCountResponse)
        return response.count
