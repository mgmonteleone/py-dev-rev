"""Article models for DevRev SDK."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import Field

from devrev.models.base import (
    CustomSchemaSpec,
    DevRevBaseModel,
    DevRevResponseModel,
    PaginatedResponse,
    SetTagWithValue,
    UserSummary,
)


class ArticleStatus(StrEnum):
    """Article status enumeration."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REVIEW_NEEDED = "review_needed"


class ArticleAccessLevel(StrEnum):
    """Article access level enumeration."""

    EXTERNAL = "external"
    INTERNAL = "internal"
    PRIVATE = "private"
    PUBLIC = "public"
    RESTRICTED = "restricted"


class ArticleType(StrEnum):
    """Article type enumeration."""

    ARTICLE = "article"
    CONTENT_BLOCK = "content_block"
    PAGE = "page"


class ArticleContentFormat(StrEnum):
    """Article content format enumeration."""

    DRDFV2 = "drdfv2"
    RT = "rt"


class CursorMode(StrEnum):
    """Cursor pagination direction."""

    AFTER = "after"
    BEFORE = "before"


class ArticleScope(DevRevResponseModel):
    """Scope/visibility level of an article.

    Values observed from the API:
    - ``{"id": 1, "label": "internal", "ordinal": 1}``
    - ``{"id": 2, "label": "external", "ordinal": 2}``
    """

    id: int = Field(..., description="Scope numeric ID (1=internal, 2=external)")
    label: str | None = Field(default=None, description="Human-readable label")
    ordinal: int | None = Field(default=None, description="Sort ordinal")


class ArticleTagSummary(DevRevResponseModel):
    """Tag summary as returned within an article's ``tags`` array."""

    id: str = Field(..., description="Tag DON ID")
    name: str | None = Field(default=None, description="Tag name")
    display_id: str | None = Field(default=None, description="Tag display ID")


class ArticleTagWithValue(DevRevResponseModel):
    """Tag entry on an article, wrapping the tag summary with an optional value."""

    tag: ArticleTagSummary = Field(..., description="Tag details")
    value: str | None = Field(default=None, description="Optional tag value")


class ArticleParentSummary(DevRevResponseModel):
    """Summary of a parent directory (collection) for an article."""

    id: str = Field(..., description="Directory DON ID")
    display_id: str | None = Field(default=None, description="Display ID")


class ArtifactSummary(DevRevResponseModel):
    """Summary of an artifact (used for extracted_content)."""

    id: str = Field(..., description="Artifact DON ID")
    display_id: str | None = Field(default=None, description="Display ID")
    file: dict[str, Any] | None = Field(default=None, description="File metadata")


class SyncMetadata(DevRevResponseModel):
    """Sync information for records synced into/from DevRev."""

    external_reference: str | None = Field(default=None, description="External record URL")
    origin_system: str | None = Field(
        default=None, description="Where the record was first created"
    )
    last_sync_in: dict[str, Any] | None = Field(
        default=None, description="Information about the sync to DevRev"
    )
    last_sync_out: dict[str, Any] | None = Field(
        default=None, description="Information about the sync from DevRev"
    )


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
    access_level: ArticleAccessLevel | None = Field(
        default=None, description="Access level (external, internal, private, public, restricted)"
    )
    aliases: list[str] | None = Field(default=None, description="Aliases of the article")
    article_type: str | None = Field(default=None, description="Article type (article, page, etc.)")
    authored_by: list[UserSummary] | None = Field(
        default=None, description="Authors of the article (API returns array, not single object)"
    )
    brand: dict[str, Any] | None = Field(
        default=None, description="Brand associated with the article"
    )
    owned_by: list[UserSummary] | None = Field(default=None, description="Owners of the article")
    created_date: datetime | None = Field(default=None, description="Creation date")
    modified_date: datetime | None = Field(default=None, description="Last modified")
    extracted_content: list[ArtifactSummary] | None = Field(
        default=None, description="Extracted content artifacts"
    )
    num_downvotes: int | None = Field(
        default=None, description="Number of downvotes on the article"
    )
    num_upvotes: int | None = Field(default=None, description="Number of upvotes on the article")
    published_at: datetime | None = Field(default=None, description="Published date of the article")
    rank: str | None = Field(default=None, description="Rank of the article")
    resource: dict[str, Any] | None = Field(
        default=None, description="Resource configuration including artifact references"
    )
    applies_to_parts: list[dict[str, Any]] | None = Field(
        default=None, description="Parts this article applies to"
    )
    scope: ArticleScope | None = Field(
        default=None, description="Visibility scope (internal/external)"
    )
    sync_metadata: SyncMetadata | None = Field(
        default=None, description="Sync information for records synced into/from DevRev"
    )
    tags: list[ArticleTagWithValue] | None = Field(
        default=None, description="Tags applied to the article"
    )
    parent: ArticleParentSummary | None = Field(
        default=None, description="Parent directory/collection"
    )
    language: str | None = Field(default=None, description="Language code (e.g., 'en')")
    url: str | None = Field(default=None, description="URL of the external article")


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


class SetSharedWithMembership(DevRevBaseModel):
    """Shared-with membership for articles."""

    member: str = Field(..., description="Member ID")
    role: str | None = Field(default=None, description="Role")


class ArticlesCreateRequest(DevRevBaseModel):
    """Request to create an article.

    Supports associating the article with parts, a parent collection (directory),
    scope (internal/external), and tags at creation time.
    """

    title: str = Field(..., description="Article title")
    description: str | None = Field(default=None, description="Article description/body")
    status: ArticleStatus | None = Field(default=None, description="Article status")
    access_level: ArticleAccessLevel | None = Field(
        default=None, description="Access level (external, internal, private, public, restricted)"
    )
    aliases: list[str] | None = Field(default=None, description="Aliases of the article (max 5)")
    authored_by: list[str] | None = Field(
        default=None, description="List of user IDs who author the article"
    )
    brand: str | None = Field(default=None, description="Brand ID associated with the article")
    content_format: ArticleContentFormat | None = Field(
        default=None, description="Content format (drdfv2, rt)"
    )
    custom_fields: dict[str, Any] | None = Field(
        default=None, description="Application-defined custom fields"
    )
    custom_schema_spec: CustomSchemaSpec | None = Field(
        default=None, description="Custom schema spec"
    )
    extracted_content: list[str] | None = Field(
        default=None, description="IDs of extracted content artifacts"
    )
    language: str | None = Field(default=None, description="Language of the article")
    notify: bool | None = Field(default=None, description="Whether to notify users when published")
    owned_by: list[str] = Field(..., description="List of dev user IDs who own the article")
    resource: dict[str, Any] = Field(
        default_factory=dict, description="Resource configuration for the article"
    )
    applies_to_parts: list[str] | None = Field(
        default=None, description="List of part IDs this article applies to"
    )
    scope: int | None = Field(default=None, description="Visibility scope: 1=internal, 2=external")
    shared_with: list[SetSharedWithMembership] | None = Field(
        default=None, description="Users/groups to share the article with"
    )
    tags: list[SetTagWithValue] | None = Field(
        default=None, description="Tags to apply (list of {'id': 'tag_id', 'value': ...})"
    )
    parent: str | None = Field(default=None, description="Parent directory/collection DON ID")
    article_type: str | None = Field(
        default=None, description="Article type: 'article' (default), 'page', 'content_block'"
    )
    published_at: datetime | None = Field(default=None, description="Published date of the article")
    release_notes: str | None = Field(default=None, description="Release notes for the article")


class ArticlesGetRequest(DevRevBaseModel):
    """Request to get an article by ID."""

    id: str = Field(..., description="Article ID")


class ArticlesDeleteRequest(DevRevBaseModel):
    """Request to delete an article."""

    id: str = Field(..., description="Article ID to delete")


class ArticlesListRequestSharedWith(DevRevBaseModel):
    """Shared-with filter for listing articles."""

    member: str | None = Field(default=None, description="Member ID filter")
    role: str | None = Field(default=None, description="Role filter")


class ArticlesListRequest(DevRevBaseModel):
    """Request to list articles."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results")
    applies_to_parts: list[str] | None = Field(default=None, description="Filter by part IDs")
    article_type: list[ArticleType] | None = Field(
        default=None, description="Filter by article types"
    )
    authored_by: list[str] | None = Field(default=None, description="Filter by author user IDs")
    brands: list[str] | None = Field(default=None, description="Filter by brand IDs")
    created_by: list[str] | None = Field(default=None, description="Filter by creator user IDs")
    mode: CursorMode | None = Field(default=None, description="Cursor pagination direction")
    modified_by: list[str] | None = Field(default=None, description="Filter by modifier user IDs")
    owned_by: list[str] | None = Field(default=None, description="Filter by owner user IDs")
    parent: list[str] | None = Field(default=None, description="Filter by parent article IDs")
    scope: list[int] | None = Field(default=None, description="Filter by scope values")
    shared_with: ArticlesListRequestSharedWith | None = Field(
        default=None, description="Filter by shared-with membership"
    )
    status: list[ArticleStatus] | None = Field(default=None, description="Filter by article status")
    tags: list[str] | None = Field(default=None, description="Filter by tag IDs")


class ArticlesUpdateRequestOwnedBy(DevRevBaseModel):
    """Owned-by update for articles."""

    set: list[str] | None = Field(default=None, description="Set owner IDs")


class ArticlesUpdateRequestAuthoredBy(DevRevBaseModel):
    """Authored-by update for articles."""

    set: list[str] | None = Field(default=None, description="Set author IDs")


class ArticlesUpdateRequestAliases(DevRevBaseModel):
    """Aliases update for articles."""

    set: list[str] | None = Field(default=None, description="Set aliases")


class ArticlesUpdateRequestAppliesToParts(DevRevBaseModel):
    """Applies-to-parts update for articles."""

    set: list[str] | None = Field(default=None, description="Set part IDs")


class ArticlesUpdateRequestTags(DevRevBaseModel):
    """Tags update for articles."""

    set: list[SetTagWithValue] | None = Field(default=None, description="Set tags")


class ArticlesUpdateRequest(DevRevBaseModel):
    """Request to update an article."""

    id: str = Field(..., description="Article ID")
    title: str | None = Field(default=None, description="New title")
    description: str | None = Field(default=None, description="New description/body")
    status: ArticleStatus | None = Field(default=None, description="New status")
    access_level: ArticleAccessLevel | None = Field(default=None, description="New access level")
    aliases: ArticlesUpdateRequestAliases | None = Field(default=None, description="New aliases")
    applies_to_parts: ArticlesUpdateRequestAppliesToParts | None = Field(
        default=None, description="New applies-to-parts"
    )
    authored_by: ArticlesUpdateRequestAuthoredBy | None = Field(
        default=None, description="New authored-by"
    )
    brand: str | None = Field(default=None, description="New brand ID")
    content_format: ArticleContentFormat | None = Field(
        default=None, description="New content format"
    )
    custom_fields: dict[str, Any] | None = Field(default=None, description="Custom fields")
    custom_schema_spec: CustomSchemaSpec | None = Field(
        default=None, description="Custom schema spec"
    )
    language: str | None = Field(default=None, description="New language code")
    notify: bool | None = Field(default=None, description="Send notifications")
    owned_by: ArticlesUpdateRequestOwnedBy | None = Field(default=None, description="New owned-by")
    parent: str | None = Field(default=None, description="New parent article ID")
    published_version: str | None = Field(default=None, description="Published version")
    release_notes: str | None = Field(default=None, description="New release notes")
    artifacts: dict[str, Any] | None = Field(
        default=None,
        description="Artifacts update using set wrapper, e.g. {'set': ['artifact_id']}",
    )
    resource: dict[str, Any] | None = Field(
        default=None,
        description="Resource configuration (read-only on updates, use artifacts instead)",
    )
    tags: ArticlesUpdateRequestTags | None = Field(default=None, description="New tags")
    url: str | None = Field(default=None, description="Article URL")


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
