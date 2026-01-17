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


class SearchResult(DevRevBaseModel):
    """Search result model."""

    id: str = Field(..., description="Result ID")
    type: str = Field(..., description="Result type")
    score: float | None = Field(default=None, description="Relevance score")
    highlights: list[str] | None = Field(default=None, description="Highlighted text snippets")
    summary: dict[str, Any] | None = Field(default=None, description="Result summary")


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
