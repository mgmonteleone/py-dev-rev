"""UOM (Unit of Measure) models for DevRev SDK.

This module contains Pydantic models for UOM-related API operations.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel, PaginatedResponse


class UomAggregationType(str, Enum):
    """UOM aggregation type enumeration."""

    SUM = "sum"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    UNIQUE_COUNT = "unique_count"
    RUNNING_TOTAL = "running_total"
    DURATION = "duration"
    LATEST = "latest"
    OLDEST = "oldest"


class UomMetricScope(str, Enum):
    """UOM metric scope enumeration."""

    ORG = "org"
    USER = "user"


class Uom(DevRevResponseModel):
    """DevRev UOM model.

    Represents a unit of measure in DevRev.
    """

    id: str = Field(..., description="UOM ID")
    display_id: str | None = Field(default=None, description="Human-readable display ID")
    name: str = Field(..., description="UOM name")
    description: str | None = Field(default=None, description="UOM description")
    aggregation_type: UomAggregationType = Field(..., description="Aggregation type")
    metric_scope: UomMetricScope | None = Field(default=None, description="Metric scope")
    dimensions: list[str] | None = Field(default=None, description="Dimensions")
    part: str | None = Field(default=None, description="Associated part ID")
    product: str | None = Field(default=None, description="Associated product ID")
    is_enabled: bool = Field(default=True, description="Whether UOM is enabled")
    created_date: datetime | None = Field(default=None, alias="created_at", description="Creation timestamp")
    modified_date: datetime | None = Field(default=None, alias="modified_at", description="Last modification timestamp")


# Request Models


class UomsCreateRequest(DevRevBaseModel):
    """Request to create a UOM."""

    name: str = Field(..., description="UOM name", min_length=1, max_length=256)
    aggregation_type: UomAggregationType = Field(..., description="Aggregation type")
    description: str | None = Field(default=None, description="UOM description", max_length=65536)
    metric_scope: UomMetricScope | None = Field(default=None, description="Metric scope")
    dimensions: list[str] | None = Field(default=None, description="Dimensions")
    part: str | None = Field(default=None, description="Associated part ID")
    product: str | None = Field(default=None, description="Associated product ID")
    is_enabled: bool = Field(default=True, description="Whether UOM is enabled")


class UomsGetRequest(DevRevBaseModel):
    """Request to get a UOM by ID."""

    id: str = Field(..., description="UOM ID")


class UomsListRequest(DevRevBaseModel):
    """Request to list UOMs."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results to return")
    aggregation_type: list[UomAggregationType] | None = Field(default=None, description="Filter by aggregation types")
    is_enabled: bool | None = Field(default=None, description="Filter by enabled status")


class UomsUpdateRequest(DevRevBaseModel):
    """Request to update a UOM."""

    id: str = Field(..., description="UOM ID")
    name: str | None = Field(default=None, description="New UOM name")
    description: str | None = Field(default=None, description="New description")
    is_enabled: bool | None = Field(default=None, description="New enabled status")


class UomsDeleteRequest(DevRevBaseModel):
    """Request to delete a UOM."""

    id: str = Field(..., description="UOM ID to delete")


class UomsCountRequest(DevRevBaseModel):
    """Request to count UOMs."""

    aggregation_type: list[UomAggregationType] | None = Field(default=None, description="Filter by aggregation types")
    is_enabled: bool | None = Field(default=None, description="Filter by enabled status")


# Response Models


class UomsCreateResponse(DevRevResponseModel):
    """Response from creating a UOM."""

    uom: Uom = Field(..., description="Created UOM")


class UomsGetResponse(DevRevResponseModel):
    """Response from getting a UOM."""

    uom: Uom = Field(..., description="Retrieved UOM")


class UomsListResponse(PaginatedResponse):
    """Response from listing UOMs."""

    uoms: list[Uom] = Field(..., description="List of UOMs")


class UomsUpdateResponse(DevRevResponseModel):
    """Response from updating a UOM."""

    uom: Uom = Field(..., description="Updated UOM")


class UomsDeleteResponse(DevRevResponseModel):
    """Response from deleting a UOM."""

    pass  # Empty response body


class UomsCountResponse(DevRevResponseModel):
    """Response from counting UOMs."""

    count: int = Field(..., description="Count of UOMs")

