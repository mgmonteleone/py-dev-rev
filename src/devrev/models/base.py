"""Base Pydantic models and configuration for DevRev SDK.

This module provides base classes and shared configuration for all models.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from devrev.models.tags import Tag


class DevRevBaseModel(BaseModel):
    """Base model for all DevRev API models.

    Provides consistent configuration across all models:
    - Strict validation
    - Extra fields forbidden
    - Alias population from camelCase
    """

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class DevRevResponseModel(DevRevBaseModel):
    """Base model for API responses.

    Allows extra fields to handle unknown API additions gracefully.
    """

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class PaginatedResponse(DevRevResponseModel):
    """Base model for paginated API responses."""

    next_cursor: str | None = Field(
        default=None,
        description="Cursor for fetching next page of results",
    )
    prev_cursor: str | None = Field(
        default=None,
        description="Cursor for fetching previous page of results",
    )


class DateFilter(DevRevBaseModel):
    """Date filter for API requests."""

    after: datetime | None = Field(
        default=None,
        description="Filter for objects after this timestamp",
    )
    before: datetime | None = Field(
        default=None,
        description="Filter for objects before this timestamp",
    )


class DateTimeFilter(DevRevBaseModel):
    """DateTime filter for API requests with preset options."""

    after: datetime | None = Field(
        default=None,
        description="Filter for objects after this timestamp",
    )
    before: datetime | None = Field(
        default=None,
        description="Filter for objects before this timestamp",
    )
    preset: str | None = Field(
        default=None,
        description="Preset time period filter",
    )


class UserSummary(DevRevResponseModel):
    """Summary of a DevRev user."""

    id: str = Field(..., description="User ID")
    display_name: str | None = Field(default=None, description="User's display name")
    email: str | None = Field(default=None, description="User's email address")
    full_name: str | None = Field(default=None, description="User's full name")


class OrgSummary(DevRevResponseModel):
    """Summary of a DevRev organization."""

    id: str = Field(..., description="Organization ID")
    display_name: str | None = Field(default=None, description="Organization's display name")


class ObjectSummary(DevRevResponseModel):
    """Summary of a generic DevRev object (used for link source/target)."""

    id: str = Field(..., description="Object ID")
    display_id: str | None = Field(default=None, description="Display ID")
    type: str | None = Field(default=None, description="Object type")


class TagWithValue(DevRevResponseModel):
    """Tag with value for resource tagging.

    Note: The API returns a full Tag object in responses (list/export endpoints),
    but may accept a string tag ID in requests. This model handles both cases.
    """

    tag: Tag | str = Field(
        ..., description="Tag object (in responses) or tag ID string (in requests)"
    )
    value: str | None = Field(default=None, description="Tag value")


class SetTagWithValue(DevRevBaseModel):
    """Tag with value for setting tags on resources."""

    id: str = Field(..., description="Tag ID")
    value: str | None = Field(default=None, description="Tag value")


class StageInfo(DevRevResponseModel):
    """Stage information for staged objects."""

    name: str | None = Field(default=None, description="Stage name")
    ordinal: int | None = Field(default=None, description="Stage ordinal position")


class StageUpdate(DevRevBaseModel):
    """Stage update request."""

    name: str | None = Field(default=None, description="Stage name to set")


class CustomSchemaSpec(DevRevBaseModel):
    """Custom schema specification."""

    validate_required_fields: bool | None = Field(
        default=None,
        description="Whether to validate required custom fields",
    )


# Common ID patterns for DevRev resources
# Format: PREFIX-XXXXX (e.g., ACC-12345, ISS-12345, DEVU-12345)
