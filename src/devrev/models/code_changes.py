"""Code Change models for DevRev SDK."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from devrev.models.base import (
    DevRevBaseModel,
    DevRevResponseModel,
    PaginatedResponse,
    UserSummary,
)


class CodeChange(DevRevResponseModel):
    """DevRev Code Change model."""

    id: str = Field(..., description="Code change ID")
    display_id: str | None = Field(default=None, description="Display ID")
    title: str | None = Field(default=None, description="Title")
    description: str | None = Field(default=None, description="Description")
    source_url: str | None = Field(default=None, description="Source URL")
    repository: str | None = Field(default=None, description="Repository")
    branch: str | None = Field(default=None, description="Branch")
    created_by: UserSummary | None = Field(default=None, description="Creator")
    created_date: datetime | None = Field(default=None, description="Creation date")
    modified_date: datetime | None = Field(default=None, description="Last modified")


class CodeChangeSummary(DevRevResponseModel):
    """Summary of a Code Change."""

    id: str = Field(..., description="Code change ID")
    title: str | None = Field(default=None, description="Title")


class CodeChangesCreateRequest(DevRevBaseModel):
    """Request to create a code change."""

    title: str = Field(..., description="Title")
    description: str | None = Field(default=None, description="Description")
    source_url: str | None = Field(default=None, description="Source URL")
    repository: str | None = Field(default=None, description="Repository")
    branch: str | None = Field(default=None, description="Branch")


class CodeChangesGetRequest(DevRevBaseModel):
    """Request to get a code change by ID."""

    id: str = Field(..., description="Code change ID")


class CodeChangesDeleteRequest(DevRevBaseModel):
    """Request to delete a code change."""

    id: str = Field(..., description="Code change ID to delete")


class CodeChangesListRequest(DevRevBaseModel):
    """Request to list code changes."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results")


class CodeChangesUpdateRequest(DevRevBaseModel):
    """Request to update a code change."""

    id: str = Field(..., description="Code change ID")
    title: str | None = Field(default=None, description="New title")
    description: str | None = Field(default=None, description="New description")


class CodeChangesCreateResponse(DevRevResponseModel):
    """Response from creating a code change."""

    code_change: CodeChange = Field(..., description="Created code change")


class CodeChangesGetResponse(DevRevResponseModel):
    """Response from getting a code change."""

    code_change: CodeChange = Field(..., description="Retrieved code change")


class CodeChangesListResponse(PaginatedResponse):
    """Response from listing code changes."""

    code_changes: list[CodeChange] = Field(..., description="List of code changes")


class CodeChangesUpdateResponse(DevRevResponseModel):
    """Response from updating a code change."""

    code_change: CodeChange = Field(..., description="Updated code change")


class CodeChangesDeleteResponse(DevRevResponseModel):
    """Response from deleting a code change."""

    pass
