"""Rev User models for DevRev SDK.

This module contains Pydantic models for Rev User-related API operations.
Rev Users are external customer users in DevRev.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field

from devrev.models.base import (
    CustomSchemaSpec,
    DateTimeFilter,
    DevRevBaseModel,
    DevRevResponseModel,
    OrgSummary,
    PaginatedResponse,
    UserSummary,
)


class RevUserState(str, Enum):
    """Rev user state enumeration.

    Values match the DevRev API 'user-state' schema.
    """

    ACTIVE = "active"
    DEACTIVATED = "deactivated"
    DELETED = "deleted"
    LOCKED = "locked"
    SHADOW = "shadow"
    UNASSIGNED = "unassigned"


class RevUser(DevRevResponseModel):
    """DevRev Rev User model.

    Represents an external customer user in DevRev.
    """

    id: str = Field(..., description="Rev user ID")
    display_id: str | None = Field(default=None, description="Human-readable display ID")
    display_name: str | None = Field(default=None, description="User's display name")
    display_picture: str | None = Field(default=None, description="Profile picture artifact ID")
    description: str | None = Field(default=None, description="User description")
    email: str | None = Field(default=None, description="Email address")
    phone_numbers: list[str] | None = Field(default=None, description="Phone numbers")
    state: RevUserState | None = Field(default=None, description="User state")
    created_date: datetime | None = Field(default=None, description="Creation timestamp")
    modified_date: datetime | None = Field(default=None, description="Last modification timestamp")
    created_by: UserSummary | None = Field(
        default=None, description="User who created this rev user"
    )
    modified_by: UserSummary | None = Field(
        default=None, description="User who last modified this rev user"
    )
    rev_org: OrgSummary | None = Field(default=None, description="Associated Rev organization")
    external_ref: str | None = Field(default=None, description="External reference identifier")
    custom_fields: dict[str, Any] | None = Field(default=None, description="Custom fields")


class RevUserSummary(DevRevResponseModel):
    """Summary of a Rev User for list/reference operations."""

    id: str = Field(..., description="Rev user ID")
    display_id: str | None = Field(default=None, description="Human-readable display ID")
    display_name: str | None = Field(default=None, description="User's display name")
    email: str | None = Field(default=None, description="Email address")
    rev_org: OrgSummary | None = Field(default=None, description="Associated Rev organization")


# Request Models


class RevUsersCreateRequest(DevRevBaseModel):
    """Request to create a Rev user."""

    rev_org: str = Field(..., description="Rev organization ID to associate with")
    description: str | None = Field(default=None, description="User description")
    display_name: str | None = Field(default=None, description="Display name")
    display_picture: str | None = Field(default=None, description="Profile picture artifact ID")
    email: str | None = Field(default=None, description="Email address")
    external_ref: str | None = Field(default=None, description="External reference identifier")
    phone_numbers: list[str] | None = Field(default=None, description="Phone numbers")
    custom_schema_spec: CustomSchemaSpec | None = Field(
        default=None, description="Custom schema spec"
    )


class RevUsersGetRequest(DevRevBaseModel):
    """Request to get a Rev user by ID."""

    id: str = Field(..., description="Rev user ID")


class RevUsersListRequest(DevRevBaseModel):
    """Request to list Rev users."""

    associations: list[str] | None = Field(
        default=None, description="Filter by account/workspace IDs"
    )
    created_by: list[str] | None = Field(default=None, description="Filter by creator user IDs")
    created_date: DateTimeFilter | None = Field(default=None, description="Filter by creation date")
    cursor: str | None = Field(default=None, description="Pagination cursor")
    email: list[str] | None = Field(default=None, description="Filter by emails")
    external_ref: list[str] | None = Field(default=None, description="Filter by external refs")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results to return")
    modified_date: DateTimeFilter | None = Field(
        default=None, description="Filter by modification date"
    )
    rev_org: list[str] | None = Field(default=None, description="Filter by Rev org IDs")
    sort_by: list[str] | None = Field(default=None, description="Sort order")


class RevUsersUpdateRequest(DevRevBaseModel):
    """Request to update a Rev user."""

    id: str = Field(..., description="Rev user ID")
    description: str | None = Field(default=None, description="New description")
    display_name: str | None = Field(default=None, description="New display name")
    display_picture: str | None = Field(default=None, description="New profile picture artifact ID")
    email: str | None = Field(default=None, description="New email address")
    external_ref: str | None = Field(default=None, description="New external reference")
    phone_numbers: list[str] | None = Field(default=None, description="New phone numbers")
    custom_fields: dict[str, Any] | None = Field(
        default=None, description="Custom fields to update"
    )


class RevUsersDeleteRequest(DevRevBaseModel):
    """Request to delete a Rev user."""

    id: str = Field(..., description="Rev user ID to delete")


class RevUsersMergeRequest(DevRevBaseModel):
    """Request to merge Rev users."""

    primary_user: str = Field(..., description="Primary user ID (will be retained)")
    secondary_user: str = Field(..., description="Secondary user ID (will be merged)")


class RevUsersAssociationsAddRequest(DevRevBaseModel):
    """Request to add associations to a Rev user (beta only)."""

    id: str = Field(..., description="Rev user ID")
    account: str | None = Field(default=None, description="Account ID to associate")
    workspace: str | None = Field(default=None, description="Workspace ID to associate")


class RevUsersAssociationsListRequest(DevRevBaseModel):
    """Request to list associations for a Rev user (beta only)."""

    id: str = Field(..., description="Rev user ID")
    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results to return")


class RevUsersAssociationsRemoveRequest(DevRevBaseModel):
    """Request to remove associations from a Rev user (beta only)."""

    id: str = Field(..., description="Rev user ID")
    account: str | None = Field(default=None, description="Account ID to remove")
    workspace: str | None = Field(default=None, description="Workspace ID to remove")


class RevUsersDeletePersonalDataRequest(DevRevBaseModel):
    """Request to delete personal data for a Rev user (beta only, GDPR compliance)."""

    id: str = Field(..., description="Rev user ID")


class RevUsersGetPersonalDataRequest(DevRevBaseModel):
    """Request to get personal data for a Rev user (beta only)."""

    id: str = Field(..., description="Rev user ID")


class RevUsersLinkRequest(DevRevBaseModel):
    """Request to link a Rev user to an organization (beta only)."""

    id: str = Field(..., description="Rev user ID")
    rev_org: str = Field(..., description="Rev organization ID to link to")


class RevUsersUnlinkRequest(DevRevBaseModel):
    """Request to unlink a Rev user from an organization (beta only)."""

    id: str = Field(..., description="Rev user ID")
    rev_org: str = Field(..., description="Rev organization ID to unlink from")


# Response Models


class RevUsersCreateResponse(DevRevResponseModel):
    """Response from creating a Rev user."""

    rev_user: RevUser = Field(..., description="Created Rev user")


class RevUsersGetResponse(DevRevResponseModel):
    """Response from getting a Rev user."""

    rev_user: RevUser = Field(..., description="Retrieved Rev user")


class RevUsersListResponse(PaginatedResponse):
    """Response from listing Rev users."""

    rev_users: list[RevUser] = Field(..., description="List of Rev users")


class RevUsersUpdateResponse(DevRevResponseModel):
    """Response from updating a Rev user."""

    rev_user: RevUser = Field(..., description="Updated Rev user")


class RevUsersDeleteResponse(DevRevResponseModel):
    """Response from deleting a Rev user."""

    pass  # Empty response body


class RevUsersMergeResponse(DevRevResponseModel):
    """Response from merging Rev users."""

    pass  # Empty response body (async processing)


class RevUsersAssociationsAddResponse(DevRevResponseModel):
    """Response from adding associations to a Rev user (beta only)."""

    pass  # Empty response body


class RevUsersAssociationsListResponse(PaginatedResponse):
    """Response from listing associations for a Rev user (beta only)."""

    associations: list[str] = Field(..., description="List of associated account/workspace IDs")


class RevUsersAssociationsRemoveResponse(DevRevResponseModel):
    """Response from removing associations from a Rev user (beta only)."""

    pass  # Empty response body


class RevUsersDeletePersonalDataResponse(DevRevResponseModel):
    """Response from deleting personal data for a Rev user (beta only)."""

    pass  # Empty response body


class RevUsersGetPersonalDataResponse(DevRevResponseModel):
    """Response from getting personal data for a Rev user (beta only)."""

    personal_data: dict[str, Any] = Field(..., description="Personal data for the user")


class RevUsersLinkResponse(DevRevResponseModel):
    """Response from linking a Rev user to an organization (beta only)."""

    pass  # Empty response body


class RevUsersUnlinkResponse(DevRevResponseModel):
    """Response from unlinking a Rev user from an organization (beta only)."""

    pass  # Empty response body
