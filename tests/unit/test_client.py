"""Unit tests for client classes."""

from devrev.client import AsyncDevRevClient, DevRevClient
from devrev.config import APIVersion, DevRevConfig


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


class TestAPIVersionPrecedence:
    """Tests for API version precedence in client initialization."""

    def test_client_default_api_version(self, mock_env_vars: dict[str, str]) -> None:
        """Test client uses default PUBLIC API version.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        client = DevRevClient()
        assert client._api_version == APIVersion.PUBLIC

    def test_client_explicit_api_version_param(self, mock_env_vars: dict[str, str]) -> None:
        """Test explicit api_version param takes effect.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        client = DevRevClient(api_version=APIVersion.BETA)
        assert client._api_version == APIVersion.BETA

    def test_client_config_api_version_overrides_param(self, mock_env_vars: dict[str, str]) -> None:
        """Test that config's api_version takes precedence when config is provided.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        config = DevRevConfig(api_version=APIVersion.BETA)
        # When config is explicitly provided, its api_version should be used
        # even if a different api_version param is passed
        client = DevRevClient(config=config, api_version=APIVersion.PUBLIC)
        assert client._api_version == APIVersion.BETA

    def test_client_config_without_explicit_param(self, mock_env_vars: dict[str, str]) -> None:
        """Test client uses config's api_version when no param provided.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        config = DevRevConfig(api_version=APIVersion.BETA)
        client = DevRevClient(config=config)
        assert client._api_version == APIVersion.BETA

    def test_async_client_default_api_version(self, mock_env_vars: dict[str, str]) -> None:
        """Test async client uses default PUBLIC API version.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        client = AsyncDevRevClient()
        assert client._api_version == APIVersion.PUBLIC

    def test_async_client_explicit_api_version(self, mock_env_vars: dict[str, str]) -> None:
        """Test async client explicit api_version param.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        client = AsyncDevRevClient(api_version=APIVersion.BETA)
        assert client._api_version == APIVersion.BETA

    def test_async_client_config_api_version_overrides_param(
        self, mock_env_vars: dict[str, str]
    ) -> None:
        """Test async client: config's api_version takes precedence.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        config = DevRevConfig(api_version=APIVersion.BETA)
        client = AsyncDevRevClient(config=config, api_version=APIVersion.PUBLIC)
        assert client._api_version == APIVersion.BETA

    def test_client_stores_api_version_separately(self, mock_env_vars: dict[str, str]) -> None:
        """Test that client stores api_version in _api_version attribute.

        Args:
            mock_env_vars: Fixture that sets up environment variables.
        """
        client = DevRevClient(api_version=APIVersion.BETA)
        # The client should have its own _api_version attribute
        assert hasattr(client, "_api_version")
        assert client._api_version == APIVersion.BETA
