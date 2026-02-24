"""Integration test fixtures for write operations.

Provides pytest fixtures for:
- Environment validation and safety checks
- DevRev client instances configured for testing
- TestDataManager instances with automatic cleanup
- Write test markers and configuration
"""

from __future__ import annotations

import logging
import os
from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest

from tests.integration.utils import TestDataManager
from tests.integration.utils.constants import (
    ENV_BASE_URL,
    ENV_TEST_API_TOKEN,
    ENV_WRITE_TESTS_ENABLED,
)

if TYPE_CHECKING:
    from devrev.client import DevRevClient

logger = logging.getLogger(__name__)


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers for integration tests."""
    config.addinivalue_line(
        "markers",
        "write: marks tests as write operation tests (create/update/delete)",
    )
    config.addinivalue_line(
        "markers",
        "slow_write: marks write tests that take longer to execute",
    )


def _validate_write_test_environment() -> None:
    """Validate environment is safe for write tests.

    Raises:
        RuntimeError: If environment is not properly configured.
    """
    base_url = os.environ.get(ENV_BASE_URL, "")
    if "prod" in base_url.lower() and "devrev" in base_url.lower():
        raise RuntimeError(
            f"Write tests cannot run against production! Current base URL: {base_url}"
        )


@pytest.fixture(scope="session")
def write_tests_enabled() -> bool:
    """Check if write tests are enabled via environment variable."""
    enabled = os.environ.get(ENV_WRITE_TESTS_ENABLED, "").lower()
    return enabled in ("true", "1", "yes")


@pytest.fixture
def skip_if_write_disabled(write_tests_enabled: bool) -> None:
    """Skip test if write tests are not enabled."""
    if not write_tests_enabled:
        pytest.skip(f"Write tests require {ENV_WRITE_TESTS_ENABLED}=true environment variable")


@pytest.fixture(scope="session")
def write_client() -> DevRevClient:
    """Create a DevRev client configured for write tests.

    Uses DEVREV_TEST_API_TOKEN if available, falls back to DEVREV_API_TOKEN.
    Validates environment safety before creating client.

    Returns:
        Configured DevRevClient instance.

    Raises:
        pytest.skip: If no API token is available.
        RuntimeError: If environment is not safe for write tests.
    """
    from devrev.client import DevRevClient

    _validate_write_test_environment()

    # Prefer dedicated test token, fall back to regular token
    token = os.environ.get(ENV_TEST_API_TOKEN) or os.environ.get("DEVREV_API_TOKEN")
    if not token:
        pytest.skip(
            f"Write tests require {ENV_TEST_API_TOKEN} or DEVREV_API_TOKEN environment variable"
        )

    logger.info("Creating DevRev client for write tests")
    return DevRevClient(api_token=token)


@pytest.fixture(scope="session")
def beta_write_client() -> DevRevClient:
    """Create a DevRev client configured for beta API write tests.

    Uses DEVREV_TEST_API_TOKEN if available, falls back to DEVREV_API_TOKEN.
    Validates environment safety before creating client.

    Returns:
        Configured DevRevClient instance with beta API.

    Raises:
        pytest.skip: If no API token is available.
        RuntimeError: If environment is not safe for write tests.
    """
    from devrev.client import DevRevClient
    from devrev.config import APIVersion

    _validate_write_test_environment()

    token = os.environ.get(ENV_TEST_API_TOKEN) or os.environ.get("DEVREV_API_TOKEN")
    if not token:
        pytest.skip(
            f"Write tests require {ENV_TEST_API_TOKEN} or DEVREV_API_TOKEN environment variable"
        )

    logger.info("Creating DevRev client for beta API write tests")
    return DevRevClient(api_token=token, api_version=APIVersion.BETA)


@pytest.fixture
def test_data(
    write_client: DevRevClient,
    skip_if_write_disabled: None,
) -> Generator[TestDataManager, None, None]:
    """Provide a TestDataManager with automatic cleanup.

    Creates a new TestDataManager for each test function,
    ensuring isolation between tests. Cleanup runs automatically
    after the test completes, even if the test fails.

    Args:
        write_client: DevRev client for API operations.
        skip_if_write_disabled: Ensures write tests are enabled.

    Yields:
        TestDataManager instance for the test.
    """
    manager = TestDataManager(write_client)
    logger.info(f"Starting test with run_id: {manager.run_id}")

    yield manager

    # Always cleanup, even on test failure
    report = manager.cleanup()
    if not report.all_succeeded:
        logger.error(f"Cleanup had failures:\n{report}")


@pytest.fixture(scope="class")
def class_test_data(
    write_client: DevRevClient,
    write_tests_enabled: bool,
) -> Generator[TestDataManager, None, None]:
    """Provide a TestDataManager shared across a test class.

    Useful for tests that need to share created resources
    across multiple test methods within the same class.

    Args:
        write_client: DevRev client for API operations.
        write_tests_enabled: Whether write tests are enabled.

    Yields:
        TestDataManager instance shared by the test class.
    """
    if not write_tests_enabled:
        pytest.skip(f"Write tests require {ENV_WRITE_TESTS_ENABLED}=true")

    manager = TestDataManager(write_client)
    logger.info(f"Starting test class with run_id: {manager.run_id}")

    yield manager

    report = manager.cleanup()
    if not report.all_succeeded:
        logger.error(f"Class cleanup had failures:\n{report}")
