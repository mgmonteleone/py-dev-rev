"""Conversation models for DevRev SDK."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from devrev.models.base import (
    DevRevBaseModel,
    DevRevResponseModel,
    PaginatedResponse,
    StageInfo,
    UserSummary,
)


class Conversation(DevRevResponseModel):
    """DevRev Conversation model."""

    id: str = Field(..., description="Conversation ID")
    display_id: str | None = Field(default=None, description="Display ID")
    title: str | None = Field(default=None, description="Title")
    description: str | None = Field(default=None, description="Description")
    stage: StageInfo | dict[str, Any] | str | None = Field(
        default=None, description="Current stage (string name or structured info)"
    )
    created_by: UserSummary | None = Field(default=None, description="Creator")
    created_date: datetime | None = Field(default=None, description="Creation date")
    modified_date: datetime | None = Field(default=None, description="Last modified")


class ConversationSummary(DevRevResponseModel):
    """Summary of a Conversation."""

    id: str = Field(..., description="Conversation ID")
    title: str | None = Field(default=None, description="Title")


class ConversationsCreateRequest(DevRevBaseModel):
    """Request to create a conversation."""

    type: str = Field(default="support", description="Conversation type")
    title: str | None = Field(default=None, description="Title")
    description: str | None = Field(default=None, description="Description")


class ConversationsGetRequest(DevRevBaseModel):
    """Request to get a conversation by ID."""

    id: str = Field(..., description="Conversation ID")


class ConversationsDeleteRequest(DevRevBaseModel):
    """Request to delete a conversation."""

    id: str = Field(..., description="Conversation ID to delete")


class ConversationsListRequest(DevRevBaseModel):
    """Request to list conversations."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results")


class ConversationsUpdateRequest(DevRevBaseModel):
    """Request to update a conversation."""

    id: str = Field(..., description="Conversation ID")
    title: str | None = Field(default=None, description="New title")
    description: str | None = Field(default=None, description="New description")


class ConversationsExportRequest(DevRevBaseModel):
    """Request to export conversations (beta only)."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results")


class ConversationsCreateResponse(DevRevResponseModel):
    """Response from creating a conversation."""

    conversation: Conversation = Field(..., description="Created conversation")


class ConversationsGetResponse(DevRevResponseModel):
    """Response from getting a conversation."""

    conversation: Conversation = Field(..., description="Retrieved conversation")


class ConversationsListResponse(PaginatedResponse):
    """Response from listing conversations."""

    conversations: list[Conversation] = Field(..., description="List of conversations")


class ConversationsUpdateResponse(DevRevResponseModel):
    """Response from updating a conversation."""

    conversation: Conversation = Field(..., description="Updated conversation")


class ConversationsDeleteResponse(DevRevResponseModel):
    """Response from deleting a conversation."""

    pass


class ConversationExportItem(DevRevResponseModel):
    """Exported conversation item (beta only)."""

    id: str = Field(..., description="Conversation ID")
    data: dict[str, object] | None = Field(default=None, description="Conversation data")


class ConversationsExportResponse(PaginatedResponse):
    """Response from exporting conversations (beta only)."""

    conversations: list[ConversationExportItem] = Field(..., description="Exported conversations")
