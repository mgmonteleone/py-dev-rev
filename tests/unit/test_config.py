"""Unit tests for configuration management."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from devrev.config import DevRevConfig, configure, get_config, reset_config


class TestDevRevConfig:
    """Tests for DevRevConfig class."""

    def test_config_loads_from_env(self, mock_env_vars: dict[str, str]) -> None:
        """Test that config loads from environment variables.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        config = DevRevConfig()

        assert config.api_token.get_secret_value() == "test-token-12345"
        assert config.base_url == "https://api.test.devrev.ai"
        assert config.timeout == 60
        assert config.log_level == "DEBUG"

    def test_config_requires_api_token(self) -> None:
        """Test that API token is required."""
        with patch.dict(os.environ, {}, clear=True), pytest.raises(ValidationError):
            DevRevConfig()

    def test_base_url_strips_trailing_slash(self, mock_env_vars: dict[str, str]) -> None:
        """Test that trailing slash is removed from base URL.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        with patch.dict(os.environ, {"DEVREV_BASE_URL": "https://api.devrev.ai/"}):
            config = DevRevConfig()
            assert config.base_url == "https://api.devrev.ai"

    def test_default_values(self, minimal_env_vars: dict[str, str]) -> None:
        """Test default configuration values.

        Args:
            minimal_env_vars: Fixture that sets up minimal environment variables.
        """
        config = DevRevConfig()

        assert config.base_url == "https://api.devrev.ai"
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.log_level == "WARN"

    def test_log_level_normalization(self, mock_env_vars: dict[str, str]) -> None:
        """Test that WARNING is normalized to WARN.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        with patch.dict(os.environ, {"DEVREV_LOG_LEVEL": "WARNING"}):
            config = DevRevConfig()
            assert config.log_level == "WARN"

    def test_api_token_is_secret(self, mock_env_vars: dict[str, str]) -> None:
        """Test that API token is properly masked.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        config = DevRevConfig()
        # SecretStr should not expose value in repr
        assert "test-token-12345" not in repr(config)
        # But should be accessible via get_secret_value
        assert config.api_token.get_secret_value() == "test-token-12345"

    def test_timeout_validation(self, mock_env_vars: dict[str, str]) -> None:
        """Test timeout range validation.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        # Valid timeout
        with patch.dict(os.environ, {"DEVREV_TIMEOUT": "100"}):
            config = DevRevConfig()
            assert config.timeout == 100

        # Invalid timeout (too high)
        with (
            patch.dict(os.environ, {"DEVREV_TIMEOUT": "500"}),
            pytest.raises(ValidationError),
        ):
            DevRevConfig()

        # Invalid timeout (too low)
        with (
            patch.dict(os.environ, {"DEVREV_TIMEOUT": "0"}),
            pytest.raises(ValidationError),
        ):
            DevRevConfig()


class TestConfigFunctions:
    """Tests for configuration helper functions."""

    def test_get_config_returns_singleton(self, mock_env_vars: dict[str, str]) -> None:
        """Test that get_config returns the same instance.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_configure_creates_new_config(self, mock_env_vars: dict[str, str]) -> None:
        """Test that configure creates a new config instance.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        config1 = get_config()
        config2 = configure(api_token="new-token", timeout=120)

        assert config1 is not config2
        assert config2.api_token.get_secret_value() == "new-token"
        assert config2.timeout == 120

    def test_reset_config_clears_singleton(self, mock_env_vars: dict[str, str]) -> None:
        """Test that reset_config clears the singleton.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        config1 = get_config()
        reset_config()
        config2 = get_config()

        # Should be different instances (singleton was reset)
        assert config1 is not config2
