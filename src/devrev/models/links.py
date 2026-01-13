"""Link models for DevRev SDK."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel, PaginatedResponse


class LinkType(str, Enum):
    """Link type enumeration."""

    IS_BLOCKED_BY = "is_blocked_by"
    IS_DEVELOPED_WITH = "is_developed_with"
    IS_DUPLICATE_OF = "is_duplicate_of"
    IS_PARENT_OF = "is_parent_of"
    IS_RELATED_TO = "is_related_to"


class Link(DevRevResponseModel):
    """DevRev Link model."""

    id: str = Field(..., description="Link ID")
    link_type: LinkType = Field(..., description="Type of link")
    source: str = Field(..., description="Source object ID")
    target: str = Field(..., description="Target object ID")
    created_date: datetime | None = Field(default=None, description="Creation date")


class LinkSummary(DevRevResponseModel):
    """Summary of a Link."""

    id: str = Field(..., description="Link ID")
    link_type: LinkType | None = Field(default=None, description="Link type")


class LinksCreateRequest(DevRevBaseModel):
    """Request to create a link."""

    link_type: LinkType = Field(..., description="Type of link")
    source: str = Field(..., description="Source object ID")
    target: str = Field(..., description="Target object ID")


class LinksGetRequest(DevRevBaseModel):
    """Request to get a link by ID."""

    id: str = Field(..., description="Link ID")


class LinksDeleteRequest(DevRevBaseModel):
    """Request to delete a link."""

    id: str = Field(..., description="Link ID to delete")


class LinksListRequest(DevRevBaseModel):
    """Request to list links."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results")
    object: str | None = Field(default=None, description="Filter by object ID")


class LinksCreateResponse(DevRevResponseModel):
    """Response from creating a link."""

    link: Link = Field(..., description="Created link")


class LinksGetResponse(DevRevResponseModel):
    """Response from getting a link."""

    link: Link = Field(..., description="Retrieved link")


class LinksListResponse(PaginatedResponse):
    """Response from listing links."""

    links: list[Link] = Field(..., description="List of links")


class LinksDeleteResponse(DevRevResponseModel):
    """Response from deleting a link."""

    pass

