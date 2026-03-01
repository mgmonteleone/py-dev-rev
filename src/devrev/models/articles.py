"""Article models for DevRev SDK."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import Field

from devrev.models.base import (
    DevRevBaseModel,
    DevRevResponseModel,
    PaginatedResponse,
    UserSummary,
)


class ArticleStatus(StrEnum):
    """Article status enumeration."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Article(DevRevResponseModel):
    """DevRev Article model.

    Note: The API returns authored_by as an array of UserSummary objects,
    not a single UserSummary object as documented in the OpenAPI spec.
    """

    id: str = Field(..., description="Article ID")
    display_id: str | None = Field(default=None, description="Display ID")
    title: str = Field(..., description="Article title")
    description: str | None = Field(default=None, description="Article description/body")
    status: ArticleStatus | None = Field(default=None, description="Article status")
    authored_by: list[UserSummary] | None = Field(
        default=None, description="Authors of the article (API returns array, not single object)"
    )
    owned_by: list[UserSummary] | None = Field(default=None, description="Owners of the article")
    created_date: datetime | None = Field(default=None, description="Creation date")
    modified_date: datetime | None = Field(default=None, description="Last modified")
    resource: dict[str, Any] | None = Field(
        default=None, description="Resource configuration including artifact references"
    )


class ArticleSummary(DevRevResponseModel):
    """Summary of an Article."""

    id: str = Field(..., description="Article ID")
    title: str | None = Field(default=None, description="Article title")


class ArticleWithContent(DevRevResponseModel):
    """Article with its content loaded.

    This model combines article metadata with the actual article body content,
    which is stored separately as an artifact in the DevRev system.
    """

    article: Article = Field(..., description="Article metadata")
    content: str = Field(..., description="Article body content")
    content_format: str = Field(default="text/plain", description="Content MIME type")
    content_version: str | None = Field(default=None, description="Artifact version")


class ArticlesCreateRequest(DevRevBaseModel):
    """Request to create an article."""

    title: str = Field(..., description="Article title")
    description: str | None = Field(default=None, description="Article description/body")
    status: ArticleStatus | None = Field(default=None, description="Article status")
    owned_by: list[str] = Field(..., description="List of dev user IDs who own the article")
    resource: dict[str, Any] = Field(
        default_factory=dict, description="Resource configuration for the article"
    )


class ArticlesGetRequest(DevRevBaseModel):
    """Request to get an article by ID."""

    id: str = Field(..., description="Article ID")


class ArticlesDeleteRequest(DevRevBaseModel):
    """Request to delete an article."""

    id: str = Field(..., description="Article ID to delete")


class ArticlesListRequest(DevRevBaseModel):
    """Request to list articles."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results")


class ArticlesUpdateRequest(DevRevBaseModel):
    """Request to update an article."""

    id: str = Field(..., description="Article ID")
    title: str | None = Field(default=None, description="New title")
    description: str | None = Field(default=None, description="New description/body")
    status: ArticleStatus | None = Field(default=None, description="New status")


class ArticlesCreateResponse(DevRevResponseModel):
    """Response from creating an article."""

    article: Article = Field(..., description="Created article")


class ArticlesGetResponse(DevRevResponseModel):
    """Response from getting an article."""

    article: Article = Field(..., description="Retrieved article")


class ArticlesListResponse(PaginatedResponse):
    """Response from listing articles."""

    articles: list[Article] = Field(..., description="List of articles")


class ArticlesUpdateResponse(DevRevResponseModel):
    """Response from updating an article."""

    article: Article = Field(..., description="Updated article")


class ArticlesDeleteResponse(DevRevResponseModel):
    """Response from deleting an article."""

    pass


class ArticlesCountRequest(DevRevBaseModel):
    """Request to count articles (beta only)."""

    status: list[str] | None = Field(default=None, description="Filter by article status")


class ArticlesCountResponse(DevRevResponseModel):
    """Response from counting articles (beta only)."""

    count: int = Field(..., description="Count of matching articles")
