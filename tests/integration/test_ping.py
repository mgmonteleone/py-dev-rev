"""Integration tests for API connectivity."""

import pytest


@pytest.mark.integration
class TestPing:
    """Test API connectivity."""

    @pytest.mark.skip(reason="Client HTTP layer not yet implemented (Phase 2)")
    def test_ping_endpoint(self) -> None:
        """Test that ping endpoint is reachable.

        This test will be enabled in Phase 2 when the HTTP client is implemented.
        """
        # This will be implemented in Phase 2
        pass
