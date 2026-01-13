"""Account models for DevRev SDK.

This module contains Pydantic models for Account-related API operations.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field

from devrev.models.base import (
    CustomSchemaSpec,
    DateFilter,
    DevRevBaseModel,
    DevRevResponseModel,
    PaginatedResponse,
    StageInfo,
    TagWithValue,
    UserSummary,
)


class AccountTier(str, Enum):
    """Account tier enumeration."""

    TIER1 = "tier-1"
    TIER2 = "tier-2"
    TIER3 = "tier-3"


class Account(DevRevResponseModel):
    """DevRev Account model.

    Represents a customer account in DevRev.
    """

    id: str = Field(..., description="Account ID")
    display_id: str | None = Field(default=None, description="Human-readable display ID")
    display_name: str | None = Field(default=None, description="Account display name")
    description: str | None = Field(default=None, description="Account description")
    created_date: datetime | None = Field(default=None, description="Creation timestamp")
    modified_date: datetime | None = Field(default=None, description="Last modification timestamp")
    created_by: UserSummary | None = Field(default=None, description="User who created the account")
    modified_by: UserSummary | None = Field(default=None, description="User who last modified the account")
    owned_by: list[UserSummary] | None = Field(default=None, description="Account owners")
    domains: list[str] | None = Field(default=None, description="Associated domains")
    external_refs: list[str] | None = Field(default=None, description="External references")
    stage: StageInfo | None = Field(default=None, description="Account stage")
    tags: list[TagWithValue] | None = Field(default=None, description="Account tags")
    tier: str | None = Field(default=None, description="Account tier")
    custom_fields: dict[str, Any] | None = Field(default=None, description="Custom fields")


class AccountSummary(DevRevResponseModel):
    """Summary of an Account for list/reference operations."""

    id: str = Field(..., description="Account ID")
    display_id: str | None = Field(default=None, description="Human-readable display ID")
    display_name: str | None = Field(default=None, description="Account display name")


# Request Models


class AccountsCreateRequest(DevRevBaseModel):
    """Request to create an account."""

    display_name: str = Field(..., description="Account display name", min_length=1, max_length=256)
    description: str | None = Field(default=None, description="Account description", max_length=65536)
    domains: list[str] | None = Field(default=None, description="Associated domains")
    external_refs: list[str] | None = Field(default=None, description="External references")
    owned_by: list[str] | None = Field(default=None, description="Owner user IDs")
    tier: str | None = Field(default=None, description="Account tier")
    custom_fields: dict[str, Any] | None = Field(default=None, description="Custom fields")
    custom_schema_spec: CustomSchemaSpec | None = Field(default=None, description="Custom schema spec")


class AccountsGetRequest(DevRevBaseModel):
    """Request to get an account by ID."""

    id: str = Field(..., description="Account ID")


class AccountsListRequest(DevRevBaseModel):
    """Request to list accounts."""

    created_by: list[str] | None = Field(default=None, description="Filter by creator user IDs")
    created_date: DateFilter | None = Field(default=None, description="Filter by creation date")
    cursor: str | None = Field(default=None, description="Pagination cursor")
    display_name: list[str] | None = Field(default=None, description="Filter by display names")
    domains: list[str] | None = Field(default=None, description="Filter by domains")
    external_refs: list[str] | None = Field(default=None, description="Filter by external refs")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results to return")
    modified_date: DateFilter | None = Field(default=None, description="Filter by modification date")
    owned_by: list[str] | None = Field(default=None, description="Filter by owner user IDs")
    sort_by: list[str] | None = Field(default=None, description="Sort order")
    stage_name: list[str] | None = Field(default=None, description="Filter by stage names")
    tags: list[str] | None = Field(default=None, description="Filter by tag IDs")


class AccountsUpdateRequest(DevRevBaseModel):
    """Request to update an account."""

    id: str = Field(..., description="Account ID")
    display_name: str | None = Field(default=None, description="New display name")
    description: str | None = Field(default=None, description="New description")
    tier: str | None = Field(default=None, description="New tier")
    custom_fields: dict[str, Any] | None = Field(default=None, description="Custom fields to update")


class AccountsDeleteRequest(DevRevBaseModel):
    """Request to delete an account."""

    id: str = Field(..., description="Account ID to delete")


class AccountsMergeRequest(DevRevBaseModel):
    """Request to merge two accounts."""

    primary_account: str = Field(..., description="Primary account ID (will be retained)")
    secondary_account: str = Field(..., description="Secondary account ID (will be merged)")


class AccountsExportRequest(DevRevBaseModel):
    """Request to export accounts."""

    created_by: list[str] | None = Field(default=None, description="Filter by creator user IDs")
    created_date: DateFilter | None = Field(default=None, description="Filter by creation date")
    first: int | None = Field(default=None, ge=1, le=10000, description="Max results")


# Response Models


class AccountsCreateResponse(DevRevResponseModel):
    """Response from creating an account."""

    account: Account = Field(..., description="Created account")


class AccountsGetResponse(DevRevResponseModel):
    """Response from getting an account."""

    account: Account = Field(..., description="Retrieved account")


class AccountsListResponse(PaginatedResponse):
    """Response from listing accounts."""

    accounts: list[Account] = Field(..., description="List of accounts")


class AccountsUpdateResponse(DevRevResponseModel):
    """Response from updating an account."""

    account: Account = Field(..., description="Updated account")


class AccountsDeleteResponse(DevRevResponseModel):
    """Response from deleting an account."""

    pass  # Empty response body


class AccountsMergeResponse(DevRevResponseModel):
    """Response from merging accounts."""

    account: Account = Field(..., description="Merged account")


class AccountsExportResponse(DevRevResponseModel):
    """Response from exporting accounts."""

    accounts: list[Account] = Field(..., description="Exported accounts")

