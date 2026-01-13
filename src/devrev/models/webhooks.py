"""Webhook models for DevRev SDK."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field

from devrev.models.base import (
    DevRevBaseModel,
    DevRevResponseModel,
    PaginatedResponse,
    UserSummary,
)


class WebhookStatus(str, Enum):
    """Webhook status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class Webhook(DevRevResponseModel):
    """DevRev Webhook model."""

    id: str = Field(..., description="Webhook ID")
    display_id: str | None = Field(default=None, description="Display ID")
    url: str = Field(..., description="Webhook URL")
    status: WebhookStatus | None = Field(default=None, description="Status")
    event_types: list[str] | None = Field(default=None, description="Event types")
    secret: str | None = Field(default=None, description="Webhook secret")
    created_date: datetime | None = Field(default=None, description="Creation date")
    modified_date: datetime | None = Field(default=None, description="Last modified")
    created_by: UserSummary | None = Field(default=None, description="Creator")


class WebhookSummary(DevRevResponseModel):
    """Summary of a Webhook."""

    id: str = Field(..., description="Webhook ID")
    url: str | None = Field(default=None, description="Webhook URL")


class WebhooksCreateRequest(DevRevBaseModel):
    """Request to create a webhook."""

    url: str = Field(..., description="Webhook URL")
    event_types: list[str] | None = Field(default=None, description="Event types")
    secret: str | None = Field(default=None, description="Webhook secret")


class WebhooksGetRequest(DevRevBaseModel):
    """Request to get a webhook by ID."""

    id: str = Field(..., description="Webhook ID")


class WebhooksDeleteRequest(DevRevBaseModel):
    """Request to delete a webhook."""

    id: str = Field(..., description="Webhook ID to delete")


class WebhooksListRequest(DevRevBaseModel):
    """Request to list webhooks."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results")


class WebhooksUpdateRequest(DevRevBaseModel):
    """Request to update a webhook."""

    id: str = Field(..., description="Webhook ID")
    url: str | None = Field(default=None, description="New URL")
    event_types: list[str] | None = Field(default=None, description="Event types")
    status: WebhookStatus | None = Field(default=None, description="New status")


class WebhooksCreateResponse(DevRevResponseModel):
    """Response from creating a webhook."""

    webhook: Webhook = Field(..., description="Created webhook")


class WebhooksGetResponse(DevRevResponseModel):
    """Response from getting a webhook."""

    webhook: Webhook = Field(..., description="Retrieved webhook")


class WebhooksListResponse(PaginatedResponse):
    """Response from listing webhooks."""

    webhooks: list[Webhook] = Field(..., description="List of webhooks")


class WebhooksUpdateResponse(DevRevResponseModel):
    """Response from updating a webhook."""

    webhook: Webhook = Field(..., description="Updated webhook")


class WebhooksDeleteResponse(DevRevResponseModel):
    """Response from deleting a webhook."""

    pass

