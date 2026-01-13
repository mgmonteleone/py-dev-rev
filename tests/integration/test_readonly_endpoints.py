"""Integration tests for read-only API endpoints.

These tests verify that list and get operations work correctly against
the actual DevRev API. They require valid API credentials set in the
environment.

To run these tests:
    export DEVREV_API_TOKEN="your-token"
    pytest tests/integration/ -v --run-integration
"""

import os

import pytest

from devrev.client import DevRevClient
from devrev.exceptions import AuthenticationError

# Skip all integration tests if DEVREV_API_TOKEN is not set
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("DEVREV_API_TOKEN"),
        reason="DEVREV_API_TOKEN environment variable not set",
    ),
]


@pytest.fixture
def client() -> DevRevClient:
    """Create a DevRev client with credentials from environment."""
    token = os.environ.get("DEVREV_API_TOKEN")
    if not token:
        pytest.skip("DEVREV_API_TOKEN not set")
    return DevRevClient(api_token=token)


class TestAccountsReadOnly:
    """Read-only tests for accounts endpoint."""

    def test_list_accounts(self, client: DevRevClient) -> None:
        """Test listing accounts (read-only)."""
        result = client.accounts.list()
        # Just verify the response is valid and returns a list
        assert hasattr(result, "accounts")
        assert isinstance(result.accounts, list)

    def test_list_accounts_with_limit(self, client: DevRevClient) -> None:
        """Test listing accounts with limit parameter."""
        result = client.accounts.list(limit=5)
        assert hasattr(result, "accounts")
        assert len(result.accounts) <= 5


class TestWorksReadOnly:
    """Read-only tests for works endpoint."""

    def test_list_works(self, client: DevRevClient) -> None:
        """Test listing work items (read-only)."""
        result = client.works.list(limit=10)
        assert hasattr(result, "works")
        assert isinstance(result.works, list)


class TestTagsReadOnly:
    """Read-only tests for tags endpoint."""

    def test_list_tags(self, client: DevRevClient) -> None:
        """Test listing tags (read-only)."""
        result = client.tags.list()
        assert hasattr(result, "tags")
        assert isinstance(result.tags, list)


class TestPartsReadOnly:
    """Read-only tests for parts endpoint."""

    def test_list_parts(self, client: DevRevClient) -> None:
        """Test listing parts (read-only)."""
        result = client.parts.list()
        assert hasattr(result, "parts")
        assert isinstance(result.parts, list)


class TestAuthenticationError:
    """Test authentication error handling."""

    def test_invalid_token_raises_error(self) -> None:
        """Test that invalid token raises AuthenticationError."""
        client = DevRevClient(api_token="invalid-token-12345")
        with pytest.raises(AuthenticationError):
            client.accounts.list()

