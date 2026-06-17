"""Part models for DevRev SDK."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field

from devrev.models.base import (
    DevRevBaseModel,
    DevRevResponseModel,
    PaginatedResponse,
    UserSummary,
)


class PartType(StrEnum):
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
    """Summary of a Part.

    This model represents the part object returned in work item responses.
    The API returns a rich object with type, display_id, name, etc.
    """

    id: str = Field(..., description="Part ID")
    type: str | None = Field(default=None, description="Part type (product, capability, etc.)")
    display_id: str | None = Field(default=None, description="Display ID (e.g., PROD-1)")
    name: str | None = Field(default=None, description="Part name")
    state: str | None = Field(default=None, description="Part state (active, archived, etc.)")
    owned_by: list[UserSummary] | None = Field(default=None, description="Part owners")


class PartsCreateRequest(DevRevBaseModel):
    """Request to create a part.

    For non-product parts (capability, feature, enhancement), the parent_part
    parameter is required to specify the parent part in the hierarchy.
    """

    name: str = Field(..., description="Part name")
    type: PartType = Field(..., description="Part type")
    description: str | None = Field(default=None, description="Description")
    owned_by: list[str] | None = Field(
        default=None,
        description="List of owner user IDs (e.g., ['DEVU-4'] or full DON IDs)",
    )
    parent_part: list[str] | None = Field(
        default=None,
        description="Parent part ID (required for capability/feature/enhancement). "
        "Array with at most 1 element.",
        max_length=1,
    )
    tags: list[str] | None = Field(default=None, description="List of tag IDs")


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


class PartsMoveRequest(DevRevBaseModel):
    """Request to move (re-parent) a part.

    The DevRev REST API only accepts ``parent_part`` on ``parts.create``, not
    ``parts.update``. This SDK-level convenience request describes a higher-level
    "move" operation that re-parents a part by recreating it under a new parent
    and relinking its dependents. It is NOT a direct DevRev API request body.
    """

    id: str = Field(..., description="ID of the part to move (re-parent)")
    new_parent_part: str = Field(
        ..., description="Target parent part ID under which the part should be moved"
    )
    dry_run: bool = Field(
        default=False,
        description="If True, compute and return the move plan without executing it",
    )


class PartsMovePlan(DevRevResponseModel):
    """Plan describing what a part move (re-parent) would do.

    Computed before (or instead of, for a dry run) executing a move so callers
    can review the dependents that will be relinked or re-parented.
    """

    source_part_id: str = Field(..., description="ID of the part to be moved")
    source_part_type: str | None = Field(
        default=None, description="Type of the source part (product, capability, etc.)"
    )
    new_parent_part: str = Field(
        ..., description="Target parent part ID the source will be moved under"
    )
    work_items_to_relink: list[str] = Field(
        default_factory=list,
        description="IDs of work items currently applies_to the source part that will be relinked",
    )
    child_parts_to_reparent: list[str] = Field(
        default_factory=list,
        description="IDs of child parts of the source that will be re-parented",
    )
    will_delete_source: bool = Field(
        default=False,
        description="Whether the original source part will be deleted after the move",
    )


class PartsMoveResult(DevRevResponseModel):
    """Outcome of an executed (or dry-run) part move (re-parent) operation."""

    new_part_id: str = Field(..., description="ID of the newly created part under the new parent")
    source_part_id: str = Field(..., description="ID of the original source part that was moved")
    relinked_work_items: list[str] = Field(
        default_factory=list,
        description="IDs of work items that were relinked from the source to the new part",
    )
    reparented_children: list[str] = Field(
        default_factory=list,
        description="IDs of child parts that were re-parented under the new part",
    )
    source_deleted: bool = Field(
        default=False, description="Whether the original source part was deleted"
    )
    dry_run: bool = Field(
        default=False,
        description="Whether this result describes a dry run (no changes were applied)",
    )
    plan: PartsMovePlan = Field(
        ..., description="The move plan that was computed for this operation"
    )
