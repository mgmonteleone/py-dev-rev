"""Part models for DevRev SDK."""

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


class PartType(str, Enum):
    """Part type enumeration."""

    PRODUCT = "product"
    CAPABILITY = "capability"
    FEATURE = "feature"
    ENHANCEMENT = "enhancement"


class Part(DevRevResponseModel):
    """DevRev Part model."""

    id: str = Field(..., description="Part ID")
    display_id: str | None = Field(default=None, description="Display ID")
    name: str = Field(..., description="Part name")
    type: PartType | None = Field(default=None, description="Part type")
    description: str | None = Field(default=None, description="Description")
    owned_by: list[UserSummary] | None = Field(default=None, description="Owners")
    created_date: datetime | None = Field(default=None, description="Creation date")
    modified_date: datetime | None = Field(default=None, description="Last modified")


class PartSummary(DevRevResponseModel):
    """Summary of a Part."""

    id: str = Field(..., description="Part ID")
    name: str | None = Field(default=None, description="Part name")


class PartsCreateRequest(DevRevBaseModel):
    """Request to create a part."""

    name: str = Field(..., description="Part name")
    type: PartType = Field(..., description="Part type")
    description: str | None = Field(default=None, description="Description")


class PartsGetRequest(DevRevBaseModel):
    """Request to get a part by ID."""

    id: str = Field(..., description="Part ID")


class PartsDeleteRequest(DevRevBaseModel):
    """Request to delete a part."""

    id: str = Field(..., description="Part ID to delete")


class PartsListRequest(DevRevBaseModel):
    """Request to list parts."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results")
    type: list[PartType] | None = Field(default=None, description="Filter by type")


class PartsUpdateRequest(DevRevBaseModel):
    """Request to update a part."""

    id: str = Field(..., description="Part ID")
    name: str | None = Field(default=None, description="New name")
    description: str | None = Field(default=None, description="New description")


class PartsCreateResponse(DevRevResponseModel):
    """Response from creating a part."""

    part: Part = Field(..., description="Created part")


class PartsGetResponse(DevRevResponseModel):
    """Response from getting a part."""

    part: Part = Field(..., description="Retrieved part")


class PartsListResponse(PaginatedResponse):
    """Response from listing parts."""

    parts: list[Part] = Field(..., description="List of parts")


class PartsUpdateResponse(DevRevResponseModel):
    """Response from updating a part."""

    part: Part = Field(..., description="Updated part")


class PartsDeleteResponse(DevRevResponseModel):
    """Response from deleting a part."""

    pass

