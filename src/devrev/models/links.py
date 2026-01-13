"""Link models for DevRev SDK."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field

from devrev.models.base import (
    DevRevBaseModel,
    DevRevResponseModel,
    ObjectSummary,
    PaginatedResponse,
)


class LinkType(str, Enum):
    """Link type enumeration.

    Note: Additional link types may exist in the API. Unknown values
    will be handled gracefully via Pydantic's extra='ignore' setting.
    """

    IS_BLOCKED_BY = "is_blocked_by"
    IS_DEPENDENT_ON = "is_dependent_on"
    IS_DEVELOPED_WITH = "is_developed_with"
    IS_DUPLICATE_OF = "is_duplicate_of"
    IS_OWNED_BY = "is_owned_by"
    IS_PARENT_OF = "is_parent_of"
    IS_PART_OF = "is_part_of"
    IS_RELATED_TO = "is_related_to"
    SERVES = "serves"


class Link(DevRevResponseModel):
    """DevRev Link model."""

    id: str = Field(..., description="Link ID")
    link_type: str = Field(..., description="Type of link (may be LinkType enum value or custom)")
    source: str | ObjectSummary | dict[str, Any] = Field(
        ..., description="Source object (ID or summary)"
    )
    target: str | ObjectSummary | dict[str, Any] = Field(
        ..., description="Target object (ID or summary)"
    )
    created_date: datetime | None = Field(default=None, description="Creation date")


class LinkSummary(DevRevResponseModel):
    """Summary of a Link."""

    id: str = Field(..., description="Link ID")
    link_type: str | None = Field(default=None, description="Link type")


class LinksCreateRequest(DevRevBaseModel):
    """Request to create a link."""

    link_type: str | LinkType = Field(..., description="Type of link")
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
