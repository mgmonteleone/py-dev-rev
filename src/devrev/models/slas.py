"""SLA models for DevRev SDK."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel, PaginatedResponse


class SlaStatus(str, Enum):
    """SLA policy status enumeration."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class SlaTrackerStatus(str, Enum):
    """SLA tracker status enumeration (for active SLA tracking)."""

    ACTIVE = "active"
    PAUSED = "paused"
    BREACHED = "breached"
    COMPLETED = "completed"


class Sla(DevRevResponseModel):
    """DevRev SLA model."""

    id: str = Field(..., description="SLA ID")
    name: str = Field(..., description="SLA name")
    description: str | None = Field(default=None, description="SLA description")
    status: str | None = Field(default=None, description="SLA status (draft/published/archived)")
    target_time: int | None = Field(default=None, description="Target time in minutes")
    created_date: datetime | None = Field(default=None, description="Creation date")
    modified_date: datetime | None = Field(default=None, description="Last modified")


class SlaSummary(DevRevResponseModel):
    """Summary of an SLA."""

    id: str = Field(..., description="SLA ID")
    name: str | None = Field(default=None, description="SLA name")


class SlasCreateRequest(DevRevBaseModel):
    """Request to create an SLA."""

    name: str = Field(..., description="SLA name")
    description: str | None = Field(default=None, description="Description")
    target_time: int | None = Field(default=None, description="Target time in minutes")


class SlasGetRequest(DevRevBaseModel):
    """Request to get an SLA by ID."""

    id: str = Field(..., description="SLA ID")


class SlasListRequest(DevRevBaseModel):
    """Request to list SLAs."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results")


class SlasUpdateRequest(DevRevBaseModel):
    """Request to update an SLA."""

    id: str = Field(..., description="SLA ID")
    name: str | None = Field(default=None, description="New name")
    description: str | None = Field(default=None, description="New description")


class SlasTransitionRequest(DevRevBaseModel):
    """Request to transition an SLA status."""

    id: str = Field(..., description="SLA ID")
    status: str | SlaStatus | SlaTrackerStatus = Field(..., description="New status")


class SlasCreateResponse(DevRevResponseModel):
    """Response from creating an SLA."""

    sla: Sla = Field(..., description="Created SLA")


class SlasGetResponse(DevRevResponseModel):
    """Response from getting an SLA."""

    sla: Sla = Field(..., description="Retrieved SLA")


class SlasListResponse(PaginatedResponse):
    """Response from listing SLAs."""

    slas: list[Sla] = Field(..., description="List of SLAs")


class SlasUpdateResponse(DevRevResponseModel):
    """Response from updating an SLA."""

    sla: Sla = Field(..., description="Updated SLA")


class SlasTransitionResponse(DevRevResponseModel):
    """Response from transitioning an SLA."""

    sla: Sla = Field(..., description="Transitioned SLA")
