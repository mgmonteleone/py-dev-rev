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


class TestSecurityFeatures:
    """Security-focused tests for configuration."""

    def test_https_required_rejects_http(self, mock_env_vars: dict[str, str]) -> None:
        """Test that HTTP URLs are rejected for security.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        with (
            patch.dict(os.environ, {"DEVREV_BASE_URL": "http://api.devrev.ai"}),
            pytest.raises(ValidationError) as exc_info,
        ):
            DevRevConfig()
        assert "Insecure HTTP URLs are not allowed" in str(exc_info.value)

    def test_https_required_accepts_https(self, mock_env_vars: dict[str, str]) -> None:
        """Test that HTTPS URLs are accepted.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        with patch.dict(os.environ, {"DEVREV_BASE_URL": "https://api.devrev.ai"}):
            config = DevRevConfig()
            assert config.base_url == "https://api.devrev.ai"

    def test_base_url_rejects_invalid_schemes(self, mock_env_vars: dict[str, str]) -> None:
        """Test that non-HTTPS schemes are rejected.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        invalid_urls = [
            "ftp://api.devrev.ai",
            "file:///etc/passwd",
            "api.devrev.ai",  # No scheme
        ]
        for url in invalid_urls:
            with (
                patch.dict(os.environ, {"DEVREV_BASE_URL": url}),
                pytest.raises(ValidationError),
            ):
                DevRevConfig()

    def test_api_token_not_in_str_repr(self, mock_env_vars: dict[str, str]) -> None:
        """Test that API token is not exposed in string representations.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        config = DevRevConfig()
        token = "test-token-12345"

        # Token should not appear in any string representation
        assert token not in str(config)
        assert token not in repr(config)
        assert token not in f"{config}"

    def test_api_token_accessible_via_secret_value(self, mock_env_vars: dict[str, str]) -> None:
        """Test that token is accessible only through get_secret_value.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        config = DevRevConfig()

        # Direct access should return SecretStr, not the value
        assert str(config.api_token) == "**********"

        # Explicit access via get_secret_value should work
        assert config.api_token.get_secret_value() == "test-token-12345"


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
