"""Work models for DevRev SDK.

This module contains Pydantic models for Work-related API operations.
Works include issues, tickets, tasks, and opportunities.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field

from devrev.models.base import (
    CustomSchemaSpec,
    DateFilter,
    DevRevBaseModel,
    DevRevResponseModel,
    PaginatedResponse,
    SetTagWithValue,
    StageInfo,
    StageUpdate,
    TagWithValue,
    UserSummary,
)
from devrev.models.parts import PartSummary


class WorkType(str, Enum):
    """Work item type enumeration."""

    ISSUE = "issue"
    TICKET = "ticket"
    TASK = "task"
    OPPORTUNITY = "opportunity"


class IssuePriority(str, Enum):
    """Issue priority enumeration."""

    P0 = "p0"
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"


class TicketSeverity(str, Enum):
    """Ticket severity enumeration."""

    BLOCKER = "blocker"
    HIGH = "high"
    LOW = "low"
    MEDIUM = "medium"


class TicketChannels(str, Enum):
    """Ticket channel enumeration."""

    EMAIL = "email"
    PLUG = "plug"
    SLACK = "slack"
    OTHER = "other"


class Work(DevRevResponseModel):
    """DevRev Work item model.

    Represents a work item (issue, ticket, task, or opportunity).
    """

    id: str = Field(..., description="Work item ID")
    type: WorkType = Field(..., description="Work item type")
    display_id: str | None = Field(default=None, description="Human-readable display ID")
    title: str | None = Field(default=None, description="Work item title")
    body: str | None = Field(default=None, description="Work item body/description")
    created_date: datetime | None = Field(default=None, description="Creation timestamp")
    modified_date: datetime | None = Field(default=None, description="Last modification timestamp")
    created_by: UserSummary | None = Field(default=None, description="User who created the work")
    modified_by: UserSummary | None = Field(
        default=None, description="User who last modified the work"
    )
    owned_by: list[UserSummary] | None = Field(default=None, description="Work owners")
    reported_by: list[UserSummary] | None = Field(
        default=None, description="Users who reported this work"
    )
    applies_to_part: PartSummary | str | None = Field(
        default=None,
        description="Part this work applies to. API returns a PartSummary object in responses.",
    )
    stage: StageInfo | None = Field(default=None, description="Work stage")
    tags: list[TagWithValue] | None = Field(default=None, description="Work tags")
    priority: str | None = Field(default=None, description="Issue priority")
    severity: str | None = Field(default=None, description="Ticket severity")
    target_close_date: datetime | None = Field(default=None, description="Target close date")
    actual_close_date: datetime | None = Field(default=None, description="Actual close date")
    custom_fields: dict[str, Any] | None = Field(default=None, description="Custom fields")
    external_ref: str | None = Field(default=None, description="External reference")


class WorkSummary(DevRevResponseModel):
    """Summary of a Work item for list/reference operations."""

    id: str = Field(..., description="Work item ID")
    type: WorkType = Field(..., description="Work item type")
    display_id: str | None = Field(default=None, description="Human-readable display ID")
    title: str | None = Field(default=None, description="Work item title")


# Request Models


class WorksCreateRequestIssue(DevRevBaseModel):
    """Issue-specific fields for work creation."""

    priority: IssuePriority | None = Field(default=None, description="Issue priority")
    priority_v2: int | None = Field(default=None, description="Priority enum ID")
    target_start_date: datetime | None = Field(default=None, description="Target start date")
    developed_with: list[str] | None = Field(
        default=None, description="Part IDs associated with issue"
    )


class WorksCreateRequestTicket(DevRevBaseModel):
    """Ticket-specific fields for work creation."""

    account: str | None = Field(default=None, description="Associated account ID")
    channels: list[TicketChannels] | None = Field(default=None, description="Ticket channels")
    rev_org: str | None = Field(default=None, description="Rev organization ID")
    severity: TicketSeverity | None = Field(default=None, description="Ticket severity")
    is_spam: bool | None = Field(default=None, description="Whether the ticket is spam")
    needs_response: bool | None = Field(default=None, description="Whether response is needed")


class WorksCreateRequest(DevRevBaseModel):
    """Request to create a work item."""

    type: WorkType = Field(..., description="Work item type")
    title: str = Field(..., description="Work title", min_length=1, max_length=256)
    applies_to_part: str = Field(..., description="Part ID this work applies to")
    owned_by: list[str] | None = Field(default=None, description="Owner user IDs")
    body: str | None = Field(default=None, description="Work body", max_length=65536)
    artifacts: list[str] | None = Field(default=None, description="Artifact IDs")
    external_ref: str | None = Field(default=None, description="External reference")
    target_close_date: datetime | None = Field(default=None, description="Target close date")
    custom_fields: dict[str, Any] | None = Field(default=None, description="Custom fields")
    custom_schema_spec: CustomSchemaSpec | None = Field(
        default=None, description="Custom schema spec"
    )
    # Issue-specific
    priority: IssuePriority | None = Field(default=None, description="Issue priority (for issues)")
    # Ticket-specific
    severity: TicketSeverity | None = Field(
        default=None, description="Ticket severity (for tickets)"
    )


class WorksGetRequest(DevRevBaseModel):
    """Request to get a work item by ID."""

    id: str = Field(..., description="Work item ID")


class WorksListRequest(DevRevBaseModel):
    """Request to list work items."""

    type: list[WorkType] | None = Field(default=None, description="Filter by work types")
    applies_to_part: list[str] | None = Field(default=None, description="Filter by part IDs")
    created_by: list[str] | None = Field(default=None, description="Filter by creator user IDs")
    created_date: DateFilter | None = Field(default=None, description="Filter by creation date")
    cursor: str | None = Field(default=None, description="Pagination cursor")
    external_ref: list[str] | None = Field(default=None, description="Filter by external refs")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results to return")
    modified_date: DateFilter | None = Field(
        default=None, description="Filter by modification date"
    )
    owned_by: list[str] | None = Field(default=None, description="Filter by owner user IDs")
    sort_by: list[str] | None = Field(default=None, description="Sort order")
    stage_name: list[str] | None = Field(default=None, description="Filter by stage names")
    target_close_date: DateFilter | None = Field(
        default=None, description="Filter by target close date"
    )


class WorksUpdateRequestOwnedBy(DevRevBaseModel):
    """Owned by update for work items."""

    set: list[str] | None = Field(default=None, description="Set owner IDs")


class WorksUpdateRequestTags(DevRevBaseModel):
    """Tags update for work items."""

    set: list[SetTagWithValue] | None = Field(default=None, description="Set tags")


class WorksUpdateRequest(DevRevBaseModel):
    """Request to update a work item."""

    id: str = Field(..., description="Work item ID")
    title: str | None = Field(default=None, description="New title")
    body: str | None = Field(default=None, description="New body")
    applies_to_part: str | None = Field(default=None, description="New part ID")
    owned_by: WorksUpdateRequestOwnedBy | None = Field(default=None, description="New owners")
    stage: StageUpdate | None = Field(default=None, description="New stage")
    tags: WorksUpdateRequestTags | None = Field(default=None, description="New tags")
    target_close_date: datetime | None = Field(default=None, description="New target close date")
    custom_fields: dict[str, Any] | None = Field(
        default=None, description="Custom fields to update"
    )
    # Issue-specific
    priority: IssuePriority | None = Field(default=None, description="New priority")
    # Ticket-specific
    severity: TicketSeverity | None = Field(default=None, description="New severity")


class WorksDeleteRequest(DevRevBaseModel):
    """Request to delete a work item."""

    id: str = Field(..., description="Work item ID to delete")


class WorksExportRequest(DevRevBaseModel):
    """Request to export work items."""

    type: list[WorkType] | None = Field(default=None, description="Filter by work types")
    applies_to_part: list[str] | None = Field(default=None, description="Filter by part IDs")
    created_by: list[str] | None = Field(default=None, description="Filter by creator user IDs")
    created_date: DateFilter | None = Field(default=None, description="Filter by creation date")
    first: int | None = Field(default=None, ge=1, le=10000, description="Max results")


class WorksCountRequest(DevRevBaseModel):
    """Request to count work items."""

    type: list[WorkType] | None = Field(default=None, description="Filter by work types")
    applies_to_part: list[str] | None = Field(default=None, description="Filter by part IDs")
    created_by: list[str] | None = Field(default=None, description="Filter by creator user IDs")
    owned_by: list[str] | None = Field(default=None, description="Filter by owner user IDs")


# Response Models


class WorksCreateResponse(DevRevResponseModel):
    """Response from creating a work item."""

    work: Work = Field(..., description="Created work item")


class WorksGetResponse(DevRevResponseModel):
    """Response from getting a work item."""

    work: Work = Field(..., description="Retrieved work item")


class WorksListResponse(PaginatedResponse):
    """Response from listing work items."""

    works: list[Work] = Field(..., description="List of work items")


class WorksUpdateResponse(DevRevResponseModel):
    """Response from updating a work item."""

    work: Work = Field(..., description="Updated work item")


class WorksDeleteResponse(DevRevResponseModel):
    """Response from deleting a work item."""

    pass  # Empty response body


class WorksExportResponse(DevRevResponseModel):
    """Response from exporting work items."""

    works: list[Work] = Field(..., description="Exported work items")


class WorksCountResponse(DevRevResponseModel):
    """Response from counting work items."""

    count: int = Field(..., description="Number of matching work items")
