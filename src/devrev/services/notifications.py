"""Notifications service for DevRev SDK."""

from __future__ import annotations

from devrev.models.notifications import (
    NotificationsSendRequest,
    NotificationsSendResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


class NotificationsService(BaseService):
    """Service for sending notifications.
    
    Provides methods to send notifications to users.
    """
    
    def send(
        self,
        recipient_id: str,
        message: str,
        *,
        title: str | None = None,
        channel: str | None = None,
    ) -> NotificationsSendResponse:
        """Send a notification.
        
        Args:
            recipient_id: ID of the recipient user
            message: Notification message content
            title: Optional notification title
            channel: Optional notification channel (email, push, etc.)
        
        Returns:
            Response indicating success and notification ID
        """
        request = NotificationsSendRequest(
            recipient_id=recipient_id,
            message=message,
            title=title,
            channel=channel,
        )
        return self._post("/notifications.send", request, NotificationsSendResponse)


class AsyncNotificationsService(AsyncBaseService):
    """Async service for sending notifications.
    
    Provides async methods to send notifications to users.
    """
    
    async def send(
        self,
        recipient_id: str,
        message: str,
        *,
        title: str | None = None,
        channel: str | None = None,
    ) -> NotificationsSendResponse:
        """Send a notification.
        
        Args:
            recipient_id: ID of the recipient user
            message: Notification message content
            title: Optional notification title
            channel: Optional notification channel (email, push, etc.)
        
        Returns:
            Response indicating success and notification ID
        """
        request = NotificationsSendRequest(
            recipient_id=recipient_id,
            message=message,
            title=title,
            channel=channel,
        )
        return await self._post("/notifications.send", request, NotificationsSendResponse)

