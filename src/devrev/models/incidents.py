"""Incident models for DevRev SDK.

This module contains Pydantic models for Incident-related API operations.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel, PaginatedResponse


class IncidentStage(str, Enum):
    """Incident stage enumeration."""

    ACKNOWLEDGED = "acknowledged"
    IDENTIFIED = "identified"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"


class IncidentSeverity(str, Enum):
    """Incident severity enumeration."""

    SEV0 = "sev0"
    SEV1 = "sev1"
    SEV2 = "sev2"
    SEV3 = "sev3"


class Incident(DevRevResponseModel):
    """DevRev Incident model.

    Represents an incident in DevRev.
    """

    id: str = Field(..., description="Incident ID")
    display_id: str | None = Field(default=None, description="Human-readable display ID")
    title: str = Field(..., description="Incident title")
    body: str | None = Field(default=None, description="Incident description")
    stage: IncidentStage | None = Field(default=None, description="Incident stage")
    severity: IncidentSeverity | None = Field(default=None, description="Incident severity")
    created_date: datetime | None = Field(default=None, alias="created_at", description="Creation timestamp")
    modified_date: datetime | None = Field(default=None, alias="modified_at", description="Last modification timestamp")
    owned_by: list[str] | None = Field(default=None, description="Owner user IDs")
    applies_to_parts: list[str] | None = Field(default=None, description="Parts this incident applies to")


class IncidentGroupItem(DevRevResponseModel):
    """Incident group item for aggregation results."""

    key: str = Field(..., description="Group key")
    count: int = Field(..., description="Count of incidents in this group")


# Request Models


class IncidentsCreateRequest(DevRevBaseModel):
    """Request to create an incident."""

    title: str = Field(..., description="Incident title", min_length=1, max_length=256)
    body: str | None = Field(default=None, description="Incident description", max_length=65536)
    severity: IncidentSeverity | None = Field(default=None, description="Incident severity")
    owned_by: list[str] | None = Field(default=None, description="Owner user IDs")
    applies_to_parts: list[str] | None = Field(default=None, description="Parts this incident applies to")


class IncidentsGetRequest(DevRevBaseModel):
    """Request to get an incident by ID."""

    id: str = Field(..., description="Incident ID")


class IncidentsListRequest(DevRevBaseModel):
    """Request to list incidents."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results to return")
    stage: list[IncidentStage] | None = Field(default=None, description="Filter by stages")
    severity: list[IncidentSeverity] | None = Field(default=None, description="Filter by severities")


class IncidentsUpdateRequest(DevRevBaseModel):
    """Request to update an incident."""

    id: str = Field(..., description="Incident ID")
    title: str | None = Field(default=None, description="New title")
    body: str | None = Field(default=None, description="New description")
    stage: IncidentStage | None = Field(default=None, description="New stage")
    severity: IncidentSeverity | None = Field(default=None, description="New severity")


class IncidentsDeleteRequest(DevRevBaseModel):
    """Request to delete an incident."""

    id: str = Field(..., description="Incident ID to delete")


class IncidentsGroupRequest(DevRevBaseModel):
    """Request to group incidents."""

    group_by: str = Field(..., description="Field to group by")
    limit: int | None = Field(default=None, ge=1, le=1000, description="Max results")


# Response Models


class IncidentsCreateResponse(DevRevResponseModel):
    """Response from creating an incident."""

    incident: Incident = Field(..., description="Created incident")


class IncidentsGetResponse(DevRevResponseModel):
    """Response from getting an incident."""

    incident: Incident = Field(..., description="Retrieved incident")


class IncidentsListResponse(PaginatedResponse):
    """Response from listing incidents."""

    incidents: list[Incident] = Field(..., description="List of incidents")


class IncidentsUpdateResponse(DevRevResponseModel):
    """Response from updating an incident."""

    incident: Incident = Field(..., description="Updated incident")


class IncidentsDeleteResponse(DevRevResponseModel):
    """Response from deleting an incident."""

    pass  # Empty response body


class IncidentsGroupResponse(DevRevResponseModel):
    """Response from grouping incidents."""

    groups: list[IncidentGroupItem] = Field(..., description="Grouped incident results")

