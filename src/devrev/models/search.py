"""Search models for DevRev SDK.

This module contains Pydantic models for Search-related API operations.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import ConfigDict, Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel


class SearchNamespace(StrEnum):
    """Search namespace enumeration — 35 supported values."""

    ACCOUNT = "account"
    ARTICLE = "article"
    CAPABILITY = "capability"
    COMPONENT = "component"
    CONVERSATION = "conversation"
    CUSTOM_OBJECT = "custom_object"
    CUSTOM_PART = "custom_part"
    CUSTOM_WORK = "custom_work"
    DASHBOARD = "dashboard"
    DATASET = "dataset"
    DEV_USER = "dev_user"
    ENHANCEMENT = "enhancement"
    FEATURE = "feature"
    GROUP = "group"
    INCIDENT = "incident"
    ISSUE = "issue"
    LINKABLE = "linkable"
    MICROSERVICE = "microservice"
    OBJECT_MEMBER = "object_member"
    OPPORTUNITY = "opportunity"
    PART = "part"
    PRODUCT = "product"
    PROJECT = "project"
    QUESTION_ANSWER = "question_answer"
    REV_ORG = "rev_org"
    REV_USER = "rev_user"
    RUNNABLE = "runnable"
    SERVICE_ACCOUNT = "service_account"
    SYS_USER = "sys_user"
    TAG = "tag"
    TASK = "task"
    TICKET = "ticket"
    USER = "user"
    VISTA = "vista"
    WIDGET = "widget"
    WORK = "work"


class SearchResult(DevRevResponseModel):
    """Individual search result from DevRev search API.

    The result contains a `type` field indicating the object type,
    a `snippet` with highlighted matching text, and a type-specific
    field containing the object data (e.g. `account`, `work`, `article`).
    """

    model_config = ConfigDict(extra="allow")

    type: str = Field(..., description="Result type (e.g. account, work, article)")
    snippet: str | None = Field(default=None, description="Text snippet with search highlights")

    # Entity-specific data - populated based on `type` field
    account: dict[str, Any] | None = Field(
        default=None, description="Account data (when type='account')"
    )
    article: dict[str, Any] | None = Field(
        default=None, description="Article data (when type='article')"
    )
    work: dict[str, Any] | None = Field(
        default=None, description="Work item data (when type='work')"
    )
    conversation: dict[str, Any] | None = Field(default=None, description="Conversation data")
    tag: dict[str, Any] | None = Field(default=None, description="Tag data (when type='tag')")
    part: dict[str, Any] | None = Field(default=None, description="Part data (when type='part')")
    rev_user: dict[str, Any] | None = Field(default=None, description="Rev user data")
    dev_user: dict[str, Any] | None = Field(default=None, description="Dev user data")
    user: dict[str, Any] | None = Field(default=None, description="User data (when type='user')")
    modified_date: str | None = Field(default=None, description="Last modified date of the result")
    comments: list[dict[str, Any]] | None = Field(
        default=None, description="Comments associated with the result"
    )


class CoreSearchRequest(DevRevBaseModel):
    """Request model for core search."""

    query: str = Field(..., description="Search query")
    namespace: SearchNamespace = Field(
        ..., description="Namespace to search (e.g. account, work, article)"
    )
    limit: int | None = Field(
        default=None,
        ge=0,
        le=50,
        description="Maximum number of results to return (API default: 10, max: 50)",
    )
    cursor: str | None = Field(default=None, description="Pagination cursor")


class HybridSearchRequest(DevRevBaseModel):
    """Request model for hybrid search."""

    query: str = Field(..., description="Search query")
    namespace: SearchNamespace = Field(
        ..., description="Namespace to search (e.g. account, work, article)"
    )
    semantic_weight: float | None = Field(
        default=None, description="Weight for semantic search (0-1)"
    )
    limit: int | None = Field(
        default=None,
        ge=0,
        le=50,
        description="Maximum number of results to return (API default: 10, max: 50)",
    )
    cursor: str | None = Field(default=None, description="Pagination cursor")


class SearchResponse(DevRevResponseModel):
    """Response model for search operations."""

    results: list[SearchResult] = Field(..., description="Search results")
    next_cursor: str | None = Field(default=None, description="Next pagination cursor")
    total_count: int | None = Field(default=None, description="Total number of results")
