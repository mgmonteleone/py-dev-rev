"""Sync and integration models for DevRev SDK.

This module contains Pydantic models for synchronization metadata
and staged object information used in external integrations.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel


class SyncStatus(str, Enum):
    """Sync status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class SyncDirection(str, Enum):
    """Sync direction enumeration."""

    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"


class SyncMetadata(DevRevResponseModel):
    """Sync metadata for external integrations.

    Tracks synchronization state between DevRev objects and
    external systems (e.g., Jira, GitHub, Salesforce).

    Attributes:
        external_id: ID in the external system
        external_url: URL to the object in the external system
        external_system: Name of the external system
        last_synced_at: Timestamp of last successful sync
        sync_status: Current sync status
        sync_direction: Direction of synchronization
        error_message: Error message if sync failed
    """

    external_id: str | None = Field(default=None, description="ID in external system")
    external_url: str | None = Field(default=None, description="URL in external system")
    external_system: str | None = Field(default=None, description="External system name")
    last_synced_at: datetime | None = Field(
        default=None, description="Last successful sync timestamp"
    )
    sync_status: SyncStatus | None = Field(default=None, description="Current sync status")
    sync_direction: SyncDirection | None = Field(default=None, description="Sync direction")
    error_message: str | None = Field(default=None, description="Error message if failed")


class StagedInfo(DevRevResponseModel):
    """Staged/draft object information.

    Represents staging information for objects that can be
    drafted before being published or committed.

    Attributes:
        is_staged: Whether the object is staged/draft
        staged_at: When the object was staged
        staged_by: User who staged the object
        publish_at: Scheduled publish time
    """

    is_staged: bool = Field(default=False, description="Whether object is staged")
    staged_at: datetime | None = Field(default=None, description="Staging timestamp")
    staged_by: str | None = Field(default=None, description="User who staged")
    publish_at: datetime | None = Field(default=None, description="Scheduled publish time")


class ExternalRef(DevRevBaseModel):
    """External reference configuration.

    Used to link DevRev objects to external systems.

    Attributes:
        external_id: ID in the external system
        external_url: URL to the external object
        system_type: Type of external system
    """

    external_id: str = Field(..., description="External system ID")
    external_url: str | None = Field(default=None, description="External URL")
    system_type: str | None = Field(default=None, description="External system type")


class SyncUnit(DevRevResponseModel):
    """Sync unit model.

    Represents a sync configuration between DevRev and an external system.

    Attributes:
        id: Unique sync unit identifier
        name: Sync unit name
        external_system: External system name
        direction: Sync direction
        status: Current status
        last_run_at: Last sync run timestamp
        next_run_at: Next scheduled run
    """

    id: str = Field(..., description="Unique sync unit identifier")
    name: str = Field(..., description="Sync unit name")
    external_system: str = Field(..., description="External system name")
    direction: SyncDirection = Field(..., description="Sync direction")
    status: SyncStatus | None = Field(default=None, description="Current status")
    last_run_at: datetime | None = Field(default=None, description="Last run timestamp")
    next_run_at: datetime | None = Field(default=None, description="Next scheduled run")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    modified_at: datetime | None = Field(default=None, description="Modification timestamp")


# Request/Response models


class SyncUnitsGetRequest(DevRevBaseModel):
    """Request to get a sync unit by ID."""

    id: str = Field(..., description="Sync unit ID")


class SyncUnitsGetResponse(DevRevResponseModel):
    """Response from getting a sync unit."""

    sync_unit: SyncUnit = Field(..., description="The sync unit")


class SyncUnitsListRequest(DevRevBaseModel):
    """Request to list sync units."""

    external_system: str | None = Field(default=None, description="Filter by system")
    status: SyncStatus | None = Field(default=None, description="Filter by status")
    limit: int | None = Field(default=None, description="Maximum results")
    cursor: str | None = Field(default=None, description="Pagination cursor")


class SyncUnitsListResponse(DevRevResponseModel):
    """Response from listing sync units."""

    sync_units: list[SyncUnit] = Field(..., description="List of sync units")
    next_cursor: str | None = Field(default=None, description="Next pagination cursor")
