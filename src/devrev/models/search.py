"""Search models for DevRev SDK.

This module contains Pydantic models for Search-related API operations.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel


class SearchNamespace(str, Enum):
    """Search namespace enumeration."""

    ACCOUNT = "account"
    ARTICLE = "article"
    CONVERSATION = "conversation"
    WORK = "work"
    USER = "user"
    TAG = "tag"
    PART = "part"
    REV_USER = "rev_user"
    DEV_USER = "dev_user"


# Search Summary Types for type-specific search results


class AccountSearchSummary(DevRevResponseModel):
    """Search summary for accounts.

    Provides a condensed view of account information in search results.
    """

    id: str = Field(..., description="Account ID")
    display_name: str = Field(..., description="Account display name")
    domains: list[str] | None = Field(default=None, description="Associated domains")
    tier: str | None = Field(default=None, description="Account tier")
    external_refs: list[str] | None = Field(default=None, description="External references")


class ArticleSearchSummary(DevRevResponseModel):
    """Search summary for articles.

    Provides a condensed view of article information in search results.
    """

    id: str = Field(..., description="Article ID")
    title: str = Field(..., description="Article title")
    status: str | None = Field(default=None, description="Article status")
    published_date: str | None = Field(default=None, description="Published date")
    author_id: str | None = Field(default=None, description="Author user ID")


class WorkSearchSummary(DevRevResponseModel):
    """Search summary for work items.

    Provides a condensed view of work item information in search results.
    """

    id: str = Field(..., description="Work item ID")
    display_id: str | None = Field(default=None, description="Display ID")
    title: str = Field(..., description="Work item title")
    type: str = Field(..., description="Work item type")
    stage: str | None = Field(default=None, description="Current stage")
    priority: str | None = Field(default=None, description="Priority level")
    owner_id: str | None = Field(default=None, description="Owner user ID")


class UserSearchSummary(DevRevResponseModel):
    """Search summary for users.

    Provides a condensed view of user information in search results.
    """

    id: str = Field(..., description="User ID")
    display_name: str = Field(..., description="User display name")
    email: str | None = Field(default=None, description="User email")
    user_type: str | None = Field(default=None, description="User type (dev/rev)")
    state: str | None = Field(default=None, description="User state")


class ConversationSearchSummary(DevRevResponseModel):
    """Search summary for conversations.

    Provides a condensed view of conversation information in search results.
    """

    id: str = Field(..., description="Conversation ID")
    title: str | None = Field(default=None, description="Conversation title")
    group_id: str | None = Field(default=None, description="Group ID")
    members_count: int | None = Field(default=None, description="Number of members")
    stage: str | None = Field(default=None, description="Conversation stage")


class PartSearchSummary(DevRevResponseModel):
    """Search summary for parts.

    Provides a condensed view of part information in search results.
    """

    id: str = Field(..., description="Part ID")
    name: str = Field(..., description="Part name")
    type: str | None = Field(default=None, description="Part type")
    owned_by_id: str | None = Field(default=None, description="Owner ID")


class TagSearchSummary(DevRevResponseModel):
    """Search summary for tags.

    Provides a condensed view of tag information in search results.
    """

    id: str = Field(..., description="Tag ID")
    name: str = Field(..., description="Tag name")
    description: str | None = Field(default=None, description="Tag description")


class SearchResult(DevRevResponseModel):
    """Search result model.

    Inherits from DevRevResponseModel to allow extra fields from API responses.
    """

    id: str = Field(..., description="Result ID")
    type: str = Field(..., description="Result type")
    score: float | None = Field(default=None, description="Relevance score")
    highlights: list[str] | None = Field(default=None, description="Highlighted text snippets")
    summary: dict[str, Any] | None = Field(default=None, description="Result summary")

    # Type-specific summaries (populated based on result type)
    account_summary: AccountSearchSummary | None = Field(
        default=None, description="Account-specific summary"
    )
    article_summary: ArticleSearchSummary | None = Field(
        default=None, description="Article-specific summary"
    )
    work_summary: WorkSearchSummary | None = Field(
        default=None, description="Work item-specific summary"
    )
    user_summary: UserSearchSummary | None = Field(
        default=None, description="User-specific summary"
    )
    conversation_summary: ConversationSearchSummary | None = Field(
        default=None, description="Conversation-specific summary"
    )
    part_summary: PartSearchSummary | None = Field(
        default=None, description="Part-specific summary"
    )
    tag_summary: TagSearchSummary | None = Field(default=None, description="Tag-specific summary")


class CoreSearchRequest(DevRevBaseModel):
    """Request model for core search."""

    query: str = Field(..., description="Search query")
    namespaces: list[SearchNamespace] | None = Field(
        default=None, description="Namespaces to search"
    )
    limit: int | None = Field(default=None, description="Maximum number of results")
    cursor: str | None = Field(default=None, description="Pagination cursor")


class HybridSearchRequest(DevRevBaseModel):
    """Request model for hybrid search."""

    query: str = Field(..., description="Search query")
    namespaces: list[SearchNamespace] | None = Field(
        default=None, description="Namespaces to search"
    )
    semantic_weight: float | None = Field(
        default=None, description="Weight for semantic search (0-1)"
    )
    limit: int | None = Field(default=None, description="Maximum number of results")
    cursor: str | None = Field(default=None, description="Pagination cursor")


class SearchResponse(DevRevResponseModel):
    """Response model for search operations."""

    results: list[SearchResult] = Field(..., description="Search results")
    next_cursor: str | None = Field(default=None, description="Next pagination cursor")
    total_count: int | None = Field(default=None, description="Total number of results")
