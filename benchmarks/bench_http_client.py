"""Benchmarks for HTTP client operations.

Run with: pytest benchmarks/bench_http_client.py --benchmark-only

Note: These benchmarks use mocked HTTP responses to measure
SDK overhead, not actual network latency.
"""

import pytest
import respx
from httpx import Response

from devrev import DevRevClient
from devrev.config import DevRevConfig


@pytest.fixture
def mock_api():
    """Create a mock API context."""
    with respx.mock(assert_all_called=False) as respx_mock:
        yield respx_mock


@pytest.fixture
def client():
    """Create a DevRev client with test config."""
    config = DevRevConfig(
        api_token="test-token",
        base_url="https://api.devrev.ai",
    )
    return DevRevClient(config=config)


class TestHttpClientBenchmarks:
    """Benchmark HTTP client operations."""

    def test_list_accounts_overhead(self, benchmark, mock_api, client):
        """Benchmark SDK overhead for list accounts."""
        mock_api.get("https://api.devrev.ai/accounts.list").mock(
            return_value=Response(
                200,
                json={
                    "accounts": [
                        {
                            "id": "don:identity:dvrv-us-1:devo/1:account/123",
                            "display_name": "Test Account",
                            "created_date": "2024-01-15T10:30:00Z",
                        }
                    ],
                    "next_cursor": None,
                },
            )
        )

        def make_request():
            return client.accounts.list(limit=10)

        benchmark(make_request)

    def test_get_work_overhead(self, benchmark, mock_api, client):
        """Benchmark SDK overhead for get work."""
        mock_api.get("https://api.devrev.ai/works.get").mock(
            return_value=Response(
                200,
                json={
                    "work": {
                        "id": "don:core:dvrv-us-1:devo/1:ticket/456",
                        "display_id": "TKT-456",
                        "type": "ticket",
                        "title": "Test Ticket",
                        "created_date": "2024-01-15T10:30:00Z",
                    }
                },
            )
        )

        def make_request():
            return client.works.get(id="don:core:dvrv-us-1:devo/1:ticket/456")

        benchmark(make_request)

    def test_create_work_overhead(self, benchmark, mock_api, client):
        """Benchmark SDK overhead for create work."""
        mock_api.post("https://api.devrev.ai/works.create").mock(
            return_value=Response(
                201,
                json={
                    "work": {
                        "id": "don:core:dvrv-us-1:devo/1:ticket/789",
                        "display_id": "TKT-789",
                        "type": "ticket",
                        "title": "New Ticket",
                        "created_date": "2024-01-15T10:30:00Z",
                    }
                },
            )
        )

        def make_request():
            return client.works.create(
                type="ticket",
                title="New Ticket",
                applies_to_part="don:core:dvrv-us-1:devo/1:part/1",
            )

        benchmark(make_request)

    def test_list_with_many_results(self, benchmark, mock_api, client):
        """Benchmark parsing many results."""
        accounts = [
            {
                "id": f"don:identity:dvrv-us-1:devo/1:account/{i}",
                "display_name": f"Account {i}",
                "created_date": "2024-01-15T10:30:00Z",
            }
            for i in range(100)
        ]

        mock_api.get("https://api.devrev.ai/accounts.list").mock(
            return_value=Response(
                200,
                json={"accounts": accounts, "next_cursor": None},
            )
        )

        def make_request():
            return client.accounts.list(limit=100)

        benchmark(make_request)

