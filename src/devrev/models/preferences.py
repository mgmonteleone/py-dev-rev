"""Preferences models for DevRev SDK."""

from __future__ import annotations

from devrev.models.base import DevRevBaseModel, DevRevResponseModel


class Preferences(DevRevResponseModel):
    """User preferences model.

    Inherits from DevRevResponseModel to allow extra fields from API responses.

    Attributes:
        id: Preferences ID
        notifications_enabled: Whether notifications are enabled
        email_notifications: Whether email notifications are enabled
        theme: UI theme preference
        locale: Locale/language preference
    """

    id: str
    notifications_enabled: bool | None = None
    email_notifications: bool | None = None
    theme: str | None = None
    locale: str | None = None


class PreferencesGetRequest(DevRevBaseModel):
    """Request to get user preferences.

    Attributes:
        user_id: Optional user ID to get preferences for
    """

    user_id: str | None = None


class PreferencesGetResponse(DevRevResponseModel):
    """Response from getting user preferences.

    Attributes:
        preferences: The user preferences
    """

    preferences: Preferences


class PreferencesUpdateRequest(DevRevBaseModel):
    """Request to update user preferences.

    Attributes:
        notifications_enabled: Whether to enable notifications
        email_notifications: Whether to enable email notifications
        theme: UI theme preference
        locale: Locale/language preference
    """

    notifications_enabled: bool | None = None
    email_notifications: bool | None = None
    theme: str | None = None
    locale: str | None = None


class PreferencesUpdateResponse(DevRevResponseModel):
    """Response from updating user preferences.

    Attributes:
        preferences: The updated preferences
    """

    preferences: Preferences
