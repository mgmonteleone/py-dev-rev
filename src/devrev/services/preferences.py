"""Preferences service for DevRev SDK."""

from __future__ import annotations

from devrev.models.preferences import (
    Preferences,
    PreferencesGetRequest,
    PreferencesGetResponse,
    PreferencesUpdateRequest,
    PreferencesUpdateResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


class PreferencesService(BaseService):
    """Service for managing user preferences.
    
    Provides methods to get and update user preferences.
    """
    
    def get(self, *, user_id: str | None = None) -> Preferences:
        """Get user preferences.
        
        Args:
            user_id: Optional user ID to get preferences for
        
        Returns:
            The user preferences
        """
        request = PreferencesGetRequest(user_id=user_id)
        response = self._post("/preferences.get", request, PreferencesGetResponse)
        return response.preferences
    
    def update(
        self,
        *,
        notifications_enabled: bool | None = None,
        email_notifications: bool | None = None,
        theme: str | None = None,
        locale: str | None = None,
    ) -> Preferences:
        """Update user preferences.
        
        Args:
            notifications_enabled: Whether to enable notifications
            email_notifications: Whether to enable email notifications
            theme: UI theme preference
            locale: Locale/language preference
        
        Returns:
            The updated preferences
        """
        request = PreferencesUpdateRequest(
            notifications_enabled=notifications_enabled,
            email_notifications=email_notifications,
            theme=theme,
            locale=locale,
        )
        response = self._post("/preferences.update", request, PreferencesUpdateResponse)
        return response.preferences


class AsyncPreferencesService(AsyncBaseService):
    """Async service for managing user preferences.
    
    Provides async methods to get and update user preferences.
    """
    
    async def get(self, *, user_id: str | None = None) -> Preferences:
        """Get user preferences.
        
        Args:
            user_id: Optional user ID to get preferences for
        
        Returns:
            The user preferences
        """
        request = PreferencesGetRequest(user_id=user_id)
        response = await self._post("/preferences.get", request, PreferencesGetResponse)
        return response.preferences
    
    async def update(
        self,
        *,
        notifications_enabled: bool | None = None,
        email_notifications: bool | None = None,
        theme: str | None = None,
        locale: str | None = None,
    ) -> Preferences:
        """Update user preferences.
        
        Args:
            notifications_enabled: Whether to enable notifications
            email_notifications: Whether to enable email notifications
            theme: UI theme preference
            locale: Locale/language preference
        
        Returns:
            The updated preferences
        """
        request = PreferencesUpdateRequest(
            notifications_enabled=notifications_enabled,
            email_notifications=email_notifications,
            theme=theme,
            locale=locale,
        )
        response = await self._post("/preferences.update", request, PreferencesUpdateResponse)
        return response.preferences

