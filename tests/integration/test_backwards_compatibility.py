"""Backwards compatibility tests for DevRev SDK.

Ensures all existing client code continues to work without modification.
This is a critical test suite - all tests must pass to maintain backwards compatibility.

Refs #93
"""

from __future__ import annotations

import pytest

from devrev import (
    APIVersion,
    AsyncDevRevClient,
    DevRevClient,
    DevRevConfig,
    configure,
    get_config,
)
from devrev.exceptions import (
    AuthenticationError,
    BetaAPIRequiredError,
    ConflictError,
    DevRevError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ServiceUnavailableError,
    ValidationError,
)


class TestBackwardsCompatibilityImports:
    """Test that all existing imports still work."""

    def test_main_module_imports(self) -> None:
        """Test that main module exports are available."""
        # These imports must not break
        from devrev import (
            AsyncDevRevClient,
            DevRevClient,
            DevRevConfig,
            configure,
            configure_logging,
            get_config,
        )

        # Verify they are the expected types
        assert DevRevClient is not None
        assert AsyncDevRevClient is not None
        assert DevRevConfig is not None
        assert callable(get_config)
        assert callable(configure)
        assert callable(configure_logging)

    def test_exception_imports(self) -> None:
        """Test that all exceptions are importable."""
        from devrev.exceptions import (
            AuthenticationError,
            ConflictError,
            DevRevError,
            ForbiddenError,
            NotFoundError,
            RateLimitError,
            ServerError,
            ServiceUnavailableError,
            ValidationError,
        )

        # All should be importable
        assert DevRevError is not None
        assert AuthenticationError is not None
        assert ForbiddenError is not None
        assert NotFoundError is not None
        assert ValidationError is not None
        assert ConflictError is not None
        assert RateLimitError is not None
        assert ServerError is not None
        assert ServiceUnavailableError is not None

    def test_model_imports(self) -> None:
        """Test that common model imports still work."""
        from devrev.models.accounts import Account
        from devrev.models.articles import Article
        from devrev.models.works import Work

        assert Account is not None
        assert Article is not None
        assert Work is not None

    def test_http_config_imports(self) -> None:
        """Test that HTTP configuration imports work."""
        from devrev import (
            CircuitBreakerConfig,
            CircuitState,
            ConnectionPoolConfig,
            TimeoutConfig,
        )

        assert TimeoutConfig is not None
        assert ConnectionPoolConfig is not None
        assert CircuitBreakerConfig is not None
        assert CircuitState is not None


class TestExceptionHierarchy:
    """Test that exception hierarchy is unchanged."""

    def test_all_exceptions_inherit_from_devrev_error(self) -> None:
        """All custom exceptions should inherit from DevRevError."""
        assert issubclass(AuthenticationError, DevRevError)
        assert issubclass(ForbiddenError, DevRevError)
        assert issubclass(NotFoundError, DevRevError)
        assert issubclass(ValidationError, DevRevError)
        assert issubclass(ConflictError, DevRevError)
        assert issubclass(RateLimitError, DevRevError)
        assert issubclass(ServerError, DevRevError)
        assert issubclass(ServiceUnavailableError, DevRevError)
        assert issubclass(BetaAPIRequiredError, DevRevError)

    def test_exceptions_are_catchable_as_devrev_error(self) -> None:
        """Catching DevRevError should catch all custom exceptions."""
        try:
            raise NotFoundError("test")
        except DevRevError as e:
            assert str(e) == "test"

        try:
            raise ValidationError("validation failed")
        except DevRevError as e:
            assert str(e) == "validation failed"


class TestClientInitialization:
    """Test that client initialization patterns still work."""

    def test_default_client_initialization(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Default client should initialize with environment variables."""
        monkeypatch.setenv("DEVREV_API_TOKEN", "test-token")

        client = DevRevClient()
        assert client is not None
        assert client.api_version == APIVersion.PUBLIC
        client.close()

    def test_client_with_explicit_token(self) -> None:
        """Client can be initialized with explicit token."""
        client = DevRevClient(api_token="test-token")
        assert client is not None
        client.close()

    def test_client_with_config_object(self) -> None:
        """Client can be initialized with DevRevConfig object."""
        config = DevRevConfig(api_token="test-token")
        client = DevRevClient(config=config)
        assert client is not None
        client.close()

    def test_async_client_initialization(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Async client should initialize the same way."""
        monkeypatch.setenv("DEVREV_API_TOKEN", "test-token")

        client = AsyncDevRevClient()
        assert client is not None
        assert client.api_version == APIVersion.PUBLIC


class TestPublicServicesAccessible:
    """Test that all public services are accessible."""

    @pytest.fixture
    def client(self) -> DevRevClient:
        """Create a test client."""
        return DevRevClient(api_token="test-token")

    def test_accounts_service_accessible(self, client: DevRevClient) -> None:
        """Accounts service should be accessible."""
        assert hasattr(client, "accounts")
        assert hasattr(client.accounts, "list")
        assert hasattr(client.accounts, "get")
        assert hasattr(client.accounts, "create")
        assert hasattr(client.accounts, "update")
        assert hasattr(client.accounts, "delete")
        client.close()

    def test_articles_service_accessible(self, client: DevRevClient) -> None:
        """Articles service should be accessible."""
        assert hasattr(client, "articles")
        assert hasattr(client.articles, "list")
        assert hasattr(client.articles, "get")
        assert hasattr(client.articles, "create")
        assert hasattr(client.articles, "update")
        assert hasattr(client.articles, "delete")
        client.close()

    def test_works_service_accessible(self, client: DevRevClient) -> None:
        """Works service should be accessible."""
        assert hasattr(client, "works")
        assert hasattr(client.works, "list")
        assert hasattr(client.works, "get")
        assert hasattr(client.works, "create")
        assert hasattr(client.works, "update")
        assert hasattr(client.works, "delete")
        client.close()

    def test_all_public_services_accessible(self, client: DevRevClient) -> None:
        """All public services should be accessible via client."""
        public_services = [
            "accounts",
            "articles",
            "code_changes",
            "conversations",
            "dev_users",
            "groups",
            "links",
            "parts",
            "rev_users",
            "slas",
            "tags",
            "timeline_entries",
            "webhooks",
            "works",
        ]
        for service_name in public_services:
            assert hasattr(client, service_name), f"Missing service: {service_name}"
            service = getattr(client, service_name)
            assert service is not None, f"Service {service_name} is None"
        client.close()


class TestBetaServicesGuarded:
    """Test that beta services are properly guarded on public API."""

    @pytest.fixture
    def public_client(self) -> DevRevClient:
        """Create a public API client."""
        return DevRevClient(api_token="test-token")

    @pytest.fixture
    def beta_client(self) -> DevRevClient:
        """Create a beta API client."""
        return DevRevClient(api_token="test-token", api_version=APIVersion.BETA)

    def test_beta_services_raise_on_public_client(self, public_client: DevRevClient) -> None:
        """Accessing beta services on public client should raise."""
        beta_services = [
            "incidents",
            "engagements",
            "brands",
            "uoms",
            "question_answers",
            "recommendations",
            "search",
            "preferences",
            "notifications",
            "track_events",
        ]
        for service_name in beta_services:
            with pytest.raises(BetaAPIRequiredError):
                getattr(public_client, service_name)
        public_client.close()

    def test_beta_services_accessible_on_beta_client(self, beta_client: DevRevClient) -> None:
        """Beta services should be accessible on beta client."""
        beta_services = [
            "incidents",
            "engagements",
            "brands",
            "uoms",
            "question_answers",
            "recommendations",
            "search",
            "preferences",
            "notifications",
            "track_events",
        ]
        for service_name in beta_services:
            service = getattr(beta_client, service_name)
            assert service is not None, f"Beta service {service_name} is None"
        beta_client.close()


class TestConfigurationCompatibility:
    """Test that configuration options remain compatible."""

    def test_config_environment_variables(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Existing environment variables should still work."""
        monkeypatch.setenv("DEVREV_API_TOKEN", "test-token")
        monkeypatch.setenv("DEVREV_BASE_URL", "https://custom.api.devrev.ai")
        monkeypatch.setenv("DEVREV_TIMEOUT", "60")
        monkeypatch.setenv("DEVREV_LOG_LEVEL", "DEBUG")

        config = DevRevConfig()
        assert config.api_token.get_secret_value() == "test-token"
        assert config.base_url == "https://custom.api.devrev.ai"
        assert config.timeout == 60
        assert config.log_level == "DEBUG"

    def test_config_direct_initialization(self) -> None:
        """Direct config initialization should work."""
        config = DevRevConfig(
            api_token="my-token",
            base_url="https://api.devrev.ai",
            timeout=45,
        )
        assert config.api_token.get_secret_value() == "my-token"
        assert config.base_url == "https://api.devrev.ai"
        assert config.timeout == 45

    def test_global_configure_function(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Global configure function should work."""
        monkeypatch.setenv("DEVREV_API_TOKEN", "test-token")

        configure(timeout=90)
        config = get_config()
        assert config.timeout == 90


class TestAPIVersionSelection:
    """Test API version selection behavior."""

    def test_default_api_version_is_public(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Default API version should be PUBLIC."""
        monkeypatch.setenv("DEVREV_API_TOKEN", "test-token")

        client = DevRevClient()
        assert client.api_version == APIVersion.PUBLIC
        client.close()

    def test_explicit_beta_version(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Explicit beta version should be respected."""
        monkeypatch.setenv("DEVREV_API_TOKEN", "test-token")

        client = DevRevClient(api_version=APIVersion.BETA)
        assert client.api_version == APIVersion.BETA
        client.close()

    def test_api_version_enum_values(self) -> None:
        """API version enum should have expected values."""
        assert APIVersion.PUBLIC.value == "public"
        assert APIVersion.BETA.value == "beta"
