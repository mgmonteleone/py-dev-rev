"""Pytest configuration and shared fixtures."""

import os
from collections.abc import Generator
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def reset_config() -> Generator[None, None, None]:
    """Reset global config between tests."""
    from devrev import config

    config.reset_config()
    yield
    config.reset_config()


@pytest.fixture
def mock_env_vars() -> Generator[dict[str, str], None, None]:
    """Provide mock environment variables for testing."""
    env_vars = {
        "DEVREV_API_TOKEN": "test-token-12345",
        "DEVREV_BASE_URL": "https://api.test.devrev.ai",
        "DEVREV_TIMEOUT": "60",
        "DEVREV_LOG_LEVEL": "DEBUG",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture
def minimal_env_vars() -> Generator[dict[str, str], None, None]:
    """Provide minimal environment variables (only required ones)."""
    env_vars = {
        "DEVREV_API_TOKEN": "test-token-minimal",
    }
    # Clear all DEVREV_ vars first, then set our minimal ones
    clean_env = {k: v for k, v in os.environ.items() if not k.startswith("DEVREV_")}
    clean_env.update(env_vars)
    with patch.dict(os.environ, clean_env, clear=True):
        yield env_vars


@pytest.fixture
def sample_config(mock_env_vars: dict[str, str]):
    """Create a sample configuration for testing.

    Args:
        mock_env_vars: Fixture that sets up environment variables (required for config).
    """
    from devrev.config import DevRevConfig

    return DevRevConfig()


# Markers for test categorization
def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may hit real API)"
    )
    config.addinivalue_line("markers", "slow: marks tests as slow running")
