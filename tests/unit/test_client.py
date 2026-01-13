"""Unit tests for client classes."""

from devrev.client import AsyncDevRevClient, DevRevClient
from devrev.config import DevRevConfig


class TestDevRevClient:
    """Tests for DevRevClient class."""

    def test_client_with_config(self, sample_config: DevRevConfig) -> None:
        """Test client initialization with config object."""
        client = DevRevClient(config=sample_config)
        assert client._config is sample_config

    def test_client_with_explicit_params(self, mock_env_vars: dict[str, str]) -> None:
        """Test client initialization with explicit parameters.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        client = DevRevClient(
            api_token="explicit-token",
            base_url="https://custom.api.devrev.ai",
            timeout=120,
        )
        assert client._config.api_token.get_secret_value() == "explicit-token"
        assert client._config.base_url == "https://custom.api.devrev.ai"
        assert client._config.timeout == 120

    def test_client_from_environment(self, mock_env_vars: dict[str, str]) -> None:
        """Test client initialization from environment.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        client = DevRevClient()
        assert client._config.api_token.get_secret_value() == "test-token-12345"

    def test_client_context_manager(self, mock_env_vars: dict[str, str]) -> None:
        """Test client as context manager.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        with DevRevClient() as client:
            assert client._config is not None


class TestAsyncDevRevClient:
    """Tests for AsyncDevRevClient class."""

    def test_async_client_with_config(self, sample_config: DevRevConfig) -> None:
        """Test async client initialization with config object."""
        client = AsyncDevRevClient(config=sample_config)
        assert client._config is sample_config

    def test_async_client_with_explicit_params(self, mock_env_vars: dict[str, str]) -> None:
        """Test async client initialization with explicit parameters.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        client = AsyncDevRevClient(
            api_token="explicit-token",
            timeout=90,
        )
        assert client._config.api_token.get_secret_value() == "explicit-token"
        assert client._config.timeout == 90
