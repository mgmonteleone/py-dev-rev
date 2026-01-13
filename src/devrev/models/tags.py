"""Tag models for DevRev SDK."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel, PaginatedResponse


class Tag(DevRevResponseModel):
    """DevRev Tag model."""

    id: str = Field(..., description="Tag ID")
    name: str = Field(..., description="Tag name")
    description: str | None = Field(default=None, description="Tag description")
    created_date: datetime | None = Field(default=None, description="Creation date")
    modified_date: datetime | None = Field(default=None, description="Last modified")


class TagSummary(DevRevResponseModel):
    """Summary of a Tag."""

    id: str = Field(..., description="Tag ID")
    name: str | None = Field(default=None, description="Tag name")


class TagsCreateRequest(DevRevBaseModel):
    """Request to create a tag."""

    name: str = Field(..., description="Tag name")
    description: str | None = Field(default=None, description="Tag description")


class TagsGetRequest(DevRevBaseModel):
    """Request to get a tag by ID."""

    id: str = Field(..., description="Tag ID")


class TagsDeleteRequest(DevRevBaseModel):
    """Request to delete a tag."""

    id: str = Field(..., description="Tag ID to delete")


class TagsListRequest(DevRevBaseModel):
    """Request to list tags."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results")


class TagsUpdateRequest(DevRevBaseModel):
    """Request to update a tag."""

    id: str = Field(..., description="Tag ID")
    name: str | None = Field(default=None, description="New name")
    description: str | None = Field(default=None, description="New description")


class TagsCreateResponse(DevRevResponseModel):
    """Response from creating a tag."""

    tag: Tag = Field(..., description="Created tag")


class TagsGetResponse(DevRevResponseModel):
    """Response from getting a tag."""

    tag: Tag = Field(..., description="Retrieved tag")


class TagsListResponse(PaginatedResponse):
    """Response from listing tags."""

    tags: list[Tag] = Field(..., description="List of tags")


class TagsUpdateResponse(DevRevResponseModel):
    """Response from updating a tag."""

    tag: Tag = Field(..., description="Updated tag")


class TagsDeleteResponse(DevRevResponseModel):
    """Response from deleting a tag."""

    pass
