"""Notifications models for DevRev SDK."""

from __future__ import annotations

from devrev.models.base import DevRevBaseModel, DevRevResponseModel


class NotificationsSendRequest(DevRevBaseModel):
    """Request to send a notification.

    Attributes:
        recipient_id: ID of the recipient user
        message: Notification message content
        title: Optional notification title
        channel: Optional notification channel (email, push, etc.)
    """

    recipient_id: str
    message: str
    title: str | None = None
    channel: str | None = None


class NotificationsSendResponse(DevRevResponseModel):
    """Response from sending a notification.

    Attributes:
        success: Whether the notification was sent successfully
        notification_id: ID of the sent notification
    """

    success: bool
    notification_id: str | None = None
