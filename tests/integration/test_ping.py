"""Integration tests for API connectivity."""

import os

import pytest

from devrev import DevRevClient


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("DEVREV_API_TOKEN"),
        reason="DEVREV_API_TOKEN environment variable not set",
    ),
]


class TestConnectivity:
    """Test API connectivity."""

    @pytest.fixture
    def client(self) -> DevRevClient:
        """Create a DevRev client."""
        return DevRevClient()

    def test_api_connectivity(self, client: DevRevClient) -> None:
        """Test that API is reachable by listing dev users.

        DevRev doesn't have a dedicated ping endpoint, so we test connectivity
        by calling dev-users.list which should always work with a valid token.
        """
        result = client.dev_users.list(limit=1)
        assert result is not None
        assert hasattr(result, "dev_users")
