"""Rev Org models for DevRev SDK.

This module contains Pydantic models for Rev Org (Revenue Organization)-related
API operations. Rev Orgs represent customer organizations in DevRev.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from devrev.models.accounts import AccountSummary
from devrev.models.base import (
    CustomSchemaSpec,
    DateFilter,
    DevRevBaseModel,
    DevRevResponseModel,
    PaginatedResponse,
    TagWithValue,
    UserSummary,
)


class RevOrg(DevRevResponseModel):
    """DevRev Rev Org (Revenue Organization) model.

    Represents a customer organization in DevRev, typically associated
    with an Account.
    """

    id: str = Field(..., description="Rev org ID")
    display_id: str | None = Field(default=None, description="Human-readable display ID")
    display_name: str | None = Field(default=None, description="Rev org display name")
    description: str | None = Field(default=None, description="Rev org description")
    account: AccountSummary | None = Field(default=None, description="Associated account")
    created_date: datetime | None = Field(default=None, description="Creation timestamp")
    modified_date: datetime | None = Field(
        default=None, description="Last modification timestamp"
    )
    created_by: UserSummary | None = Field(
        default=None, description="User who created this rev org"
    )
    modified_by: UserSummary | None = Field(
        default=None, description="User who last modified this rev org"
    )
    domain: str | None = Field(default=None, description="Domain")
    external_ref: str | None = Field(
        default=None, description="External reference identifier"
    )
    external_refs: list[str] | None = Field(
        default=None, description="External references"
    )
    custom_fields: dict[str, Any] | None = Field(
        default=None, description="Custom fields"
    )
    sub_type: str | None = Field(default=None, description="Rev org subtype")
    tags: list[TagWithValue] | None = Field(default=None, description="Tags")
    tier: str | None = Field(default=None, description="Rev org tier")
    artifacts: list[str] | None = Field(
        default=None, description="Associated artifact IDs"
    )


class RevOrgSummary(DevRevResponseModel):
    """Summary of a Rev Org for list/reference operations."""

    id: str = Field(..., description="Rev org ID")
    display_id: str | None = Field(default=None, description="Human-readable display ID")
    display_name: str | None = Field(default=None, description="Rev org display name")


# Request Models


class RevOrgsGetRequest(DevRevBaseModel):
    """Request to get a rev org."""

    id: str | None = Field(default=None, description="Rev org ID")
    account: str | None = Field(
        default=None, description="Account ID to get the default rev org for"
    )


class RevOrgsListRequest(DevRevBaseModel):
    """Request to list rev orgs."""

    account: list[str] | None = Field(default=None, description="Filter by account IDs")
    created_by: list[str] | None = Field(
        default=None, description="Filter by creator user IDs"
    )
    created_date: DateFilter | None = Field(
        default=None, description="Filter by creation date"
    )
    cursor: str | None = Field(default=None, description="Pagination cursor")
    display_name: list[str] | None = Field(
        default=None, description="Filter by display names"
    )
    domains: list[str] | None = Field(default=None, description="Filter by domains")
    external_refs: list[str] | None = Field(
        default=None, description="Filter by external refs"
    )
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results to return")
    modified_date: DateFilter | None = Field(
        default=None, description="Filter by modification date"
    )
    owned_by: list[str] | None = Field(
        default=None, description="Filter by owner user IDs"
    )
    tags: list[str] | None = Field(default=None, description="Filter by tag IDs")


class RevOrgsCreateRequest(DevRevBaseModel):
    """Request to create a rev org."""

    display_name: str = Field(
        ..., description="Rev org display name", min_length=1, max_length=256
    )
    account: str = Field(..., description="Parent account ID")
    description: str | None = Field(default=None, description="Rev org description")
    external_ref: str | None = Field(
        default=None, description="External reference identifier"
    )
    tier: str | None = Field(default=None, description="Rev org tier")
    custom_fields: dict[str, Any] | None = Field(
        default=None, description="Custom fields"
    )
    custom_schema_spec: CustomSchemaSpec | None = Field(
        default=None, description="Custom schema spec"
    )


class RevOrgsUpdateRequest(DevRevBaseModel):
    """Request to update a rev org."""

    id: str = Field(..., description="Rev org ID")
    display_name: str | None = Field(default=None, description="New display name")
    description: str | None = Field(default=None, description="New description")
    tier: str | None = Field(default=None, description="New tier")
    custom_fields: dict[str, Any] | None = Field(
        default=None, description="Custom fields to update"
    )
    artifacts: dict[str, Any] | None = Field(
        default=None, description="Artifact set/remove operations"
    )


class RevOrgsDeleteRequest(DevRevBaseModel):
    """Request to delete a rev org."""

    id: str = Field(..., description="Rev org ID to delete")


# Response Models


class RevOrgsGetResponse(DevRevResponseModel):
    """Response from getting a rev org."""

    rev_org: RevOrg = Field(..., description="Retrieved rev org")


class RevOrgsListResponse(PaginatedResponse):
    """Response from listing rev orgs."""

    rev_orgs: list[RevOrg] = Field(..., description="List of rev orgs")


class RevOrgsCreateResponse(DevRevResponseModel):
    """Response from creating a rev org."""

    rev_org: RevOrg = Field(..., description="Created rev org")


class RevOrgsUpdateResponse(DevRevResponseModel):
    """Response from updating a rev org."""

    rev_org: RevOrg = Field(..., description="Updated rev org")


class RevOrgsDeleteResponse(DevRevResponseModel):
    """Response from deleting a rev org."""

    pass  # Empty response body
