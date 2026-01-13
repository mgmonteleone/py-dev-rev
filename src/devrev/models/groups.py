"""Group models for DevRev SDK."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field

from devrev.models.base import (
    DevRevBaseModel,
    DevRevResponseModel,
    PaginatedResponse,
    UserSummary,
)


class GroupType(str, Enum):
    """Group type enumeration."""

    STATIC = "static"
    DYNAMIC = "dynamic"


class Group(DevRevResponseModel):
    """DevRev Group model."""

    id: str = Field(..., description="Group ID")
    name: str = Field(..., description="Group name")
    description: str | None = Field(default=None, description="Description")
    type: GroupType | None = Field(default=None, description="Group type")
    created_date: datetime | None = Field(default=None, description="Creation date")
    modified_date: datetime | None = Field(default=None, description="Last modified")


class GroupSummary(DevRevResponseModel):
    """Summary of a Group."""

    id: str = Field(..., description="Group ID")
    name: str | None = Field(default=None, description="Group name")


class GroupMember(DevRevResponseModel):
    """Group member model."""

    id: str = Field(..., description="Member ID")
    member: UserSummary | None = Field(default=None, description="Member details")


class GroupsCreateRequest(DevRevBaseModel):
    """Request to create a group."""

    name: str = Field(..., description="Group name")
    description: str | None = Field(default=None, description="Description")
    type: GroupType | None = Field(default=None, description="Group type")


class GroupsGetRequest(DevRevBaseModel):
    """Request to get a group by ID."""

    id: str = Field(..., description="Group ID")


class GroupsListRequest(DevRevBaseModel):
    """Request to list groups."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results")


class GroupsUpdateRequest(DevRevBaseModel):
    """Request to update a group."""

    id: str = Field(..., description="Group ID")
    name: str | None = Field(default=None, description="New name")
    description: str | None = Field(default=None, description="New description")


class GroupMembersAddRequest(DevRevBaseModel):
    """Request to add members to a group."""

    group: str = Field(..., description="Group ID")
    member: str = Field(..., description="Member ID to add")


class GroupMembersRemoveRequest(DevRevBaseModel):
    """Request to remove members from a group."""

    group: str = Field(..., description="Group ID")
    member: str = Field(..., description="Member ID to remove")


class GroupMembersListRequest(DevRevBaseModel):
    """Request to list group members."""

    group: str = Field(..., description="Group ID")
    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results")


class GroupsCreateResponse(DevRevResponseModel):
    """Response from creating a group."""

    group: Group = Field(..., description="Created group")


class GroupsGetResponse(DevRevResponseModel):
    """Response from getting a group."""

    group: Group = Field(..., description="Retrieved group")


class GroupsListResponse(PaginatedResponse):
    """Response from listing groups."""

    groups: list[Group] = Field(..., description="List of groups")


class GroupsUpdateResponse(DevRevResponseModel):
    """Response from updating a group."""

    group: Group = Field(..., description="Updated group")


class GroupMembersAddResponse(DevRevResponseModel):
    """Response from adding members."""

    pass


class GroupMembersRemoveResponse(DevRevResponseModel):
    """Response from removing members."""

    pass


class GroupMembersListResponse(PaginatedResponse):
    """Response from listing members."""

    members: list[GroupMember] = Field(..., description="List of members")
