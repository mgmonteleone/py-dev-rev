"""Unit tests for PreferencesService.

Refs #92
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from devrev.models.preferences import Preferences
from devrev.services.preferences import AsyncPreferencesService, PreferencesService

from .conftest import create_mock_response


class TestPreferencesService:
    """Tests for PreferencesService."""

    def test_get_preferences_without_user_id(
        self,
        mock_http_client: MagicMock,
        sample_preferences_data: dict[str, Any],
    ) -> None:
        """Test getting preferences without specifying user ID."""
        mock_http_client.post.return_value = create_mock_response(
            {"preferences": sample_preferences_data}
        )

        service = PreferencesService(mock_http_client)
        result = service.get()

        assert isinstance(result, Preferences)
        assert result.id == "don:identity:preferences:123"
        assert result.notifications_enabled is True
        assert result.email_notifications is True
        assert result.theme == "dark"
        assert result.locale == "en-US"
        mock_http_client.post.assert_called_once()

    def test_get_preferences_with_user_id(
        self,
        mock_http_client: MagicMock,
        sample_preferences_data: dict[str, Any],
    ) -> None:
        """Test getting preferences for a specific user."""
        mock_http_client.post.return_value = create_mock_response(
            {"preferences": sample_preferences_data}
        )

        service = PreferencesService(mock_http_client)
        result = service.get(user_id="don:identity:user:456")

        assert isinstance(result, Preferences)
        assert result.id == "don:identity:preferences:123"
        mock_http_client.post.assert_called_once()

    def test_update_preferences_all_fields(
        self,
        mock_http_client: MagicMock,
        sample_preferences_data: dict[str, Any],
    ) -> None:
        """Test updating all preference fields."""
        updated_data = {
            **sample_preferences_data,
            "notifications_enabled": False,
            "email_notifications": False,
            "theme": "light",
            "locale": "fr-FR",
        }
        mock_http_client.post.return_value = create_mock_response({"preferences": updated_data})

        service = PreferencesService(mock_http_client)
        result = service.update(
            notifications_enabled=False,
            email_notifications=False,
            theme="light",
            locale="fr-FR",
        )

        assert isinstance(result, Preferences)
        assert result.notifications_enabled is False
        assert result.email_notifications is False
        assert result.theme == "light"
        assert result.locale == "fr-FR"
        mock_http_client.post.assert_called_once()

    def test_update_preferences_partial(
        self,
        mock_http_client: MagicMock,
        sample_preferences_data: dict[str, Any],
    ) -> None:
        """Test updating only some preference fields."""
        updated_data = {**sample_preferences_data, "theme": "light"}
        mock_http_client.post.return_value = create_mock_response({"preferences": updated_data})

        service = PreferencesService(mock_http_client)
        result = service.update(theme="light")

        assert isinstance(result, Preferences)
        assert result.theme == "light"
        # Other fields should remain unchanged
        assert result.notifications_enabled is True
        assert result.email_notifications is True
        mock_http_client.post.assert_called_once()

    def test_update_preferences_notifications_only(
        self,
        mock_http_client: MagicMock,
        sample_preferences_data: dict[str, Any],
    ) -> None:
        """Test updating only notification preferences."""
        updated_data = {
            **sample_preferences_data,
            "notifications_enabled": False,
        }
        mock_http_client.post.return_value = create_mock_response({"preferences": updated_data})

        service = PreferencesService(mock_http_client)
        result = service.update(notifications_enabled=False)

        assert isinstance(result, Preferences)
        assert result.notifications_enabled is False
        mock_http_client.post.assert_called_once()


@pytest.mark.asyncio
class TestAsyncPreferencesService:
    """Tests for AsyncPreferencesService."""

    async def test_get_preferences_without_user_id(
        self,
        mock_async_http_client: AsyncMock,
        sample_preferences_data: dict[str, Any],
    ) -> None:
        """Test getting preferences without specifying user ID (async)."""
        mock_async_http_client.post.return_value = create_mock_response(
            {"preferences": sample_preferences_data}
        )

        service = AsyncPreferencesService(mock_async_http_client)
        result = await service.get()

        assert isinstance(result, Preferences)
        assert result.id == "don:identity:preferences:123"
        assert result.notifications_enabled is True
        assert result.email_notifications is True
        assert result.theme == "dark"
        assert result.locale == "en-US"
        mock_async_http_client.post.assert_called_once()

    async def test_get_preferences_with_user_id(
        self,
        mock_async_http_client: AsyncMock,
        sample_preferences_data: dict[str, Any],
    ) -> None:
        """Test getting preferences for a specific user (async)."""
        mock_async_http_client.post.return_value = create_mock_response(
            {"preferences": sample_preferences_data}
        )

        service = AsyncPreferencesService(mock_async_http_client)
        result = await service.get(user_id="don:identity:user:456")

        assert isinstance(result, Preferences)
        assert result.id == "don:identity:preferences:123"
        mock_async_http_client.post.assert_called_once()

    async def test_update_preferences_all_fields(
        self,
        mock_async_http_client: AsyncMock,
        sample_preferences_data: dict[str, Any],
    ) -> None:
        """Test updating all preference fields (async)."""
        updated_data = {
            **sample_preferences_data,
            "notifications_enabled": False,
            "email_notifications": False,
            "theme": "light",
            "locale": "fr-FR",
        }
        mock_async_http_client.post.return_value = create_mock_response(
            {"preferences": updated_data}
        )

        service = AsyncPreferencesService(mock_async_http_client)
        result = await service.update(
            notifications_enabled=False,
            email_notifications=False,
            theme="light",
            locale="fr-FR",
        )

        assert isinstance(result, Preferences)
        assert result.notifications_enabled is False
        assert result.email_notifications is False
        assert result.theme == "light"
        assert result.locale == "fr-FR"
        mock_async_http_client.post.assert_called_once()

    async def test_update_preferences_partial(
        self,
        mock_async_http_client: AsyncMock,
        sample_preferences_data: dict[str, Any],
    ) -> None:
        """Test updating only some preference fields (async)."""
        updated_data = {**sample_preferences_data, "theme": "light"}
        mock_async_http_client.post.return_value = create_mock_response(
            {"preferences": updated_data}
        )

        service = AsyncPreferencesService(mock_async_http_client)
        result = await service.update(theme="light")

        assert isinstance(result, Preferences)
        assert result.theme == "light"
        # Other fields should remain unchanged
        assert result.notifications_enabled is True
        assert result.email_notifications is True
        mock_async_http_client.post.assert_called_once()

    async def test_update_preferences_notifications_only(
        self,
        mock_async_http_client: AsyncMock,
        sample_preferences_data: dict[str, Any],
    ) -> None:
        """Test updating only notification preferences (async)."""
        updated_data = {
            **sample_preferences_data,
            "notifications_enabled": False,
        }
        mock_async_http_client.post.return_value = create_mock_response(
            {"preferences": updated_data}
        )

        service = AsyncPreferencesService(mock_async_http_client)
        result = await service.update(notifications_enabled=False)

        assert isinstance(result, Preferences)
        assert result.notifications_enabled is False
        mock_async_http_client.post.assert_called_once()
