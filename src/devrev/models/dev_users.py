"""Dev User models for DevRev SDK.

This module contains Pydantic models for Dev User-related API operations.
Dev Users are internal organization users in DevRev.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import Field

from devrev.models.base import (
    CustomSchemaSpec,
    DateFilter,
    DevRevBaseModel,
    DevRevResponseModel,
    PaginatedResponse,
    UserSummary,
)


class DevUserState(StrEnum):
    """Dev user state enumeration.

    Values match the DevRev API 'user-state' schema.
    """

    ACTIVE = "active"
    DEACTIVATED = "deactivated"
    DELETED = "deleted"
    LOCKED = "locked"
    SHADOW = "shadow"
    UNASSIGNED = "unassigned"


class DevUserExternalIdentity(DevRevResponseModel):
    """External identity linked to a Dev user."""

    id: str = Field(..., description="External identity ID")
    issuer: str = Field(..., description="Identity issuer")
    display_name: str | None = Field(default=None, description="Display name in external source")


class DevUser(DevRevResponseModel):
    """DevRev Dev User model.

    Represents an internal organization user in DevRev.
    """

    id: str = Field(..., description="Dev user ID")
    display_id: str | None = Field(default=None, description="Human-readable display ID")
    display_name: str | None = Field(default=None, description="User's display name")
    display_picture: dict[str, Any] | str | None = Field(
        default=None, description="Profile picture artifact reference or ID"
    )
    email: str | None = Field(default=None, description="Email address")
    full_name: str | None = Field(default=None, description="Full name")
    phone_numbers: list[str] | None = Field(default=None, description="Phone numbers")
    state: DevUserState | None = Field(default=None, description="User state")
    created_date: datetime | None = Field(default=None, description="Creation timestamp")
    modified_date: datetime | None = Field(default=None, description="Last modification timestamp")
    external_identities: list[DevUserExternalIdentity] | None = Field(
        default=None, description="Linked external identities"
    )
    reports_to: UserSummary | None = Field(default=None, description="Manager")
    custom_fields: dict[str, Any] | None = Field(default=None, description="Custom fields")


class DevUserSummary(DevRevResponseModel):
    """Summary of a Dev User for list/reference operations."""

    id: str = Field(..., description="Dev user ID")
    display_id: str | None = Field(default=None, description="Human-readable display ID")
    display_name: str | None = Field(default=None, description="User's display name")
    email: str | None = Field(default=None, description="Email address")


# Request Models


class DevUserExternalIdentityFilter(DevRevBaseModel):
    """Filter for Dev user external identity."""

    id: str | None = Field(default=None, description="External identity ID")
    issuer: str | None = Field(default=None, description="Identity issuer")


class DevUsersCreateRequestStateEnum(StrEnum):
    """Allowed states for Dev user creation."""

    SHADOW = "shadow"


class DevUsersCreateRequest(DevRevBaseModel):
    """Request to create a Dev user."""

    email: str = Field(..., description="Email address")
    state: DevUsersCreateRequestStateEnum = Field(
        ..., description="Initial user state (must be shadow)"
    )
    display_name: str | None = Field(default=None, description="Display name")
    full_name: str | None = Field(default=None, description="Full name")
    reports_to: str | None = Field(default=None, description="Manager user ID")
    custom_fields: dict[str, Any] | None = Field(default=None, description="Custom fields")
    custom_schema_spec: CustomSchemaSpec | None = Field(
        default=None, description="Custom schema spec"
    )


class DevUsersGetRequest(DevRevBaseModel):
    """Request to get a Dev user by ID."""

    id: str = Field(..., description="Dev user ID")


class DevUsersListRequest(DevRevBaseModel):
    """Request to list Dev users."""

    created_date: DateFilter | None = Field(default=None, description="Filter by creation date")
    cursor: str | None = Field(default=None, description="Pagination cursor")
    email: list[str] | None = Field(default=None, description="Filter by emails")
    external_identity: list[DevUserExternalIdentityFilter] | None = Field(
        default=None, description="Filter by external identity"
    )
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results to return")
    modified_date: DateFilter | None = Field(
        default=None, description="Filter by modification date"
    )
    phone_numbers: list[str] | None = Field(default=None, description="Filter by phone numbers")
    sort_by: list[str] | None = Field(default=None, description="Sort order")
    state: list[DevUserState] | None = Field(default=None, description="Filter by states")


class DevUsersUpdateRequest(DevRevBaseModel):
    """Request to update a Dev user."""

    id: str = Field(..., description="Dev user ID")
    display_name: str | None = Field(default=None, description="New display name")
    display_picture: str | None = Field(default=None, description="New profile picture artifact ID")
    full_name: str | None = Field(default=None, description="New full name")
    reports_to: str | None = Field(default=None, description="New manager user ID")
    custom_fields: dict[str, Any] | None = Field(
        default=None, description="Custom fields to update"
    )


class DevUsersActivateRequest(DevRevBaseModel):
    """Request to activate a Dev user."""

    id: str = Field(..., description="Dev user ID")


class DevUsersDeactivateRequest(DevRevBaseModel):
    """Request to deactivate a Dev user."""

    id: str = Field(..., description="Dev user ID")


class DevUsersIdentitiesLinkRequest(DevRevBaseModel):
    """Request to link an external identity to a Dev user."""

    dev_user: str = Field(..., description="Dev user ID")
    id: str = Field(..., description="External identity ID")
    issuer: str = Field(..., description="Identity issuer")
    display_name: str | None = Field(default=None, description="Display name in external source")


class DevUsersIdentitiesUnlinkRequest(DevRevBaseModel):
    """Request to unlink an external identity from a Dev user."""

    dev_user: str = Field(..., description="Dev user ID")
    id: str = Field(..., description="External identity ID")
    issuer: str = Field(..., description="Identity issuer")


class DevUsersSelfUpdateRequest(DevRevBaseModel):
    """Request to update the authenticated user."""

    display_name: str | None = Field(default=None, description="New display name")
    display_picture: str | None = Field(default=None, description="New profile picture artifact ID")
    full_name: str | None = Field(default=None, description="New full name")


class DevUsersSelfRequest(DevRevBaseModel):
    """Request to get the authenticated user (self)."""

    pass  # Empty request body


class DevUsersMergeRequest(DevRevBaseModel):
    """Request to merge two Dev users."""

    primary_user: str = Field(..., description="Primary user ID (will be retained)")
    secondary_user: str = Field(..., description="Secondary user ID (will be merged)")


# Response Models


class DevUsersCreateResponse(DevRevResponseModel):
    """Response from creating a Dev user."""

    dev_user: DevUser = Field(..., description="Created Dev user")


class DevUsersGetResponse(DevRevResponseModel):
    """Response from getting a Dev user."""

    dev_user: DevUser = Field(..., description="Retrieved Dev user")


class DevUsersListResponse(PaginatedResponse):
    """Response from listing Dev users."""

    dev_users: list[DevUser] = Field(..., description="List of Dev users")


class DevUsersUpdateResponse(DevRevResponseModel):
    """Response from updating a Dev user."""

    dev_user: DevUser = Field(..., description="Updated Dev user")


class DevUsersActivateResponse(DevRevResponseModel):
    """Response from activating a Dev user."""

    dev_user: DevUser = Field(..., description="Activated Dev user")


class DevUsersDeactivateResponse(DevRevResponseModel):
    """Response from deactivating a Dev user."""

    pass  # Empty response body


class DevUsersIdentitiesLinkResponse(DevRevResponseModel):
    """Response from linking an external identity."""

    dev_user: DevUser = Field(..., description="Updated Dev user")


class DevUsersIdentitiesUnlinkResponse(DevRevResponseModel):
    """Response from unlinking an external identity."""

    dev_user: DevUser = Field(..., description="Updated Dev user")


class DevUsersMergeResponse(DevRevResponseModel):
    """Response from merging Dev users."""

    pass  # Empty response body


class DevUsersSelfResponse(DevRevResponseModel):
    """Response from getting the authenticated user."""

    dev_user: DevUser = Field(..., description="Authenticated Dev user")


class DevUsersSelfUpdateResponse(DevRevResponseModel):
    """Response from updating the authenticated user."""

    dev_user: DevUser = Field(..., description="Updated Dev user")
