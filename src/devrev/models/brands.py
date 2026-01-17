"""Brand models for DevRev SDK.

This module contains Pydantic models for Brand-related API operations.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel, PaginatedResponse


class Brand(DevRevResponseModel):
    """DevRev Brand model.

    Represents a brand in DevRev.
    """

    id: str = Field(..., description="Brand ID")
    display_id: str | None = Field(default=None, description="Human-readable display ID")
    name: str = Field(..., description="Brand name")
    description: str | None = Field(default=None, description="Brand description")
    logo_url: str | None = Field(default=None, description="Brand logo URL")
    created_date: datetime | None = Field(
        default=None, alias="created_at", description="Creation timestamp"
    )
    modified_date: datetime | None = Field(
        default=None, alias="modified_at", description="Last modification timestamp"
    )


# Request Models


class BrandsCreateRequest(DevRevBaseModel):
    """Request to create a brand."""

    name: str = Field(..., description="Brand name", min_length=1, max_length=256)
    description: str | None = Field(default=None, description="Brand description", max_length=65536)
    logo_url: str | None = Field(default=None, description="Brand logo URL")


class BrandsGetRequest(DevRevBaseModel):
    """Request to get a brand by ID."""

    id: str = Field(..., description="Brand ID")


class BrandsListRequest(DevRevBaseModel):
    """Request to list brands."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results to return")


class BrandsUpdateRequest(DevRevBaseModel):
    """Request to update a brand."""

    id: str = Field(..., description="Brand ID")
    name: str | None = Field(default=None, description="New brand name")
    description: str | None = Field(default=None, description="New description")
    logo_url: str | None = Field(default=None, description="New logo URL")


class BrandsDeleteRequest(DevRevBaseModel):
    """Request to delete a brand."""

    id: str = Field(..., description="Brand ID to delete")


# Response Models


class BrandsCreateResponse(DevRevResponseModel):
    """Response from creating a brand."""

    brand: Brand = Field(..., description="Created brand")


class BrandsGetResponse(DevRevResponseModel):
    """Response from getting a brand."""

    brand: Brand = Field(..., description="Retrieved brand")


class BrandsListResponse(PaginatedResponse):
    """Response from listing brands."""

    brands: list[Brand] = Field(..., description="List of brands")


class BrandsUpdateResponse(DevRevResponseModel):
    """Response from updating a brand."""

    brand: Brand = Field(..., description="Updated brand")


class BrandsDeleteResponse(DevRevResponseModel):
    """Response from deleting a brand."""

    pass  # Empty response body
