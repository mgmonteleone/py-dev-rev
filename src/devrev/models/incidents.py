"""Incident models for DevRev SDK.

This module contains Pydantic models for Incident-related API operations.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel, PaginatedResponse


class IncidentStage(str, Enum):
    """Incident stage enumeration (for request filters)."""

    ACKNOWLEDGED = "acknowledged"
    IDENTIFIED = "identified"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"


class IncidentSeverity(str, Enum):
    """Incident severity enumeration (for request filters)."""

    SEV0 = "sev0"
    SEV1 = "sev1"
    SEV2 = "sev2"
    SEV3 = "sev3"


class EnumValue(DevRevResponseModel):
    """Represents an enum value from DevRev API."""

    id: int | None = Field(default=None, description="Unique ID of the enum value")
    label: str | None = Field(default=None, description="Display label of the enum value")
    ordinal: int | None = Field(default=None, description="Order of the enum value")


class CustomStageSummary(DevRevResponseModel):
    """Summary of a custom stage."""

    id: str | None = Field(default=None, description="Stage ID")
    name: str | None = Field(default=None, description="Stage name")


class CustomStateSummary(DevRevResponseModel):
    """Summary of a custom state."""

    id: str | None = Field(default=None, description="State ID")
    name: str | None = Field(default=None, description="State name")
    is_final: bool | None = Field(default=None, description="Whether this is a final state")


class Stage(DevRevResponseModel):
    """Describes the current stage of an object."""

    stage: CustomStageSummary | None = Field(default=None, description="Current stage")
    state: CustomStateSummary | None = Field(default=None, description="Current state")


class Incident(DevRevResponseModel):
    """DevRev Incident model.

    Represents an incident in DevRev.
    """

    id: str = Field(..., description="Incident ID")
    display_id: str | None = Field(default=None, description="Human-readable display ID")
    title: str | None = Field(default=None, description="Incident title")
    body: str | None = Field(default=None, description="Incident description")
    stage: Stage | dict[str, Any] | None = Field(default=None, description="Incident stage")
    severity: EnumValue | dict[str, Any] | None = Field(
        default=None, description="Incident severity"
    )
    created_date: datetime | None = Field(default=None, description="Creation timestamp")
    modified_date: datetime | None = Field(default=None, description="Last modification timestamp")
    identified_date: datetime | None = Field(
        default=None, description="Time when incident was identified"
    )
    owned_by: list[Any] | None = Field(default=None, description="Owner users")
    applies_to_parts: list[Any] | None = Field(
        default=None, description="Parts this incident applies to"
    )


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
    applies_to_parts: list[str] | None = Field(
        default=None, description="Parts this incident applies to"
    )


class IncidentsGetRequest(DevRevBaseModel):
    """Request to get an incident by ID."""

    id: str = Field(..., description="Incident ID")


class IncidentsListRequest(DevRevBaseModel):
    """Request to list incidents."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results to return")
    stage: list[IncidentStage] | None = Field(default=None, description="Filter by stages")
    severity: list[IncidentSeverity] | None = Field(
        default=None, description="Filter by severities"
    )


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
