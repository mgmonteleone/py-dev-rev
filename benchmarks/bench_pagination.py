"""Benchmarks for pagination operations.

Run with: pytest benchmarks/bench_pagination.py --benchmark-only

Note: These benchmarks use mocked HTTP responses.
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


def create_paginated_responses(pages: int, items_per_page: int):
    """Create a sequence of paginated responses."""
    responses = []
    for page in range(pages):
        cursor = f"cursor_{page + 1}" if page < pages - 1 else None
        accounts = [
            {
                "id": f"don:identity:dvrv-us-1:devo/1:account/{page * items_per_page + i}",
                "display_name": f"Account {page * items_per_page + i}",
                "created_date": "2024-01-15T10:30:00Z",
            }
            for i in range(items_per_page)
        ]
        responses.append({"accounts": accounts, "next_cursor": cursor})
    return responses


class TestPaginationBenchmarks:
    """Benchmark pagination operations."""

    def test_single_page_10_items(self, benchmark, mock_api, client):
        """Benchmark single page with 10 items."""
        responses = create_paginated_responses(1, 10)
        mock_api.post("https://api.devrev.ai/accounts.list").mock(
            return_value=Response(200, json=responses[0])
        )

        def fetch_all():
            return client.accounts.list(limit=10)

        benchmark(fetch_all)

    def test_single_page_100_items(self, benchmark, mock_api, client):
        """Benchmark single page with 100 items."""
        responses = create_paginated_responses(1, 100)
        mock_api.post("https://api.devrev.ai/accounts.list").mock(
            return_value=Response(200, json=responses[0])
        )

        def fetch_all():
            return client.accounts.list(limit=100)

        benchmark(fetch_all)

    def test_paginate_10_pages(self, benchmark, mock_api, client):
        """Benchmark 10 pages of 100 items each."""
        responses = create_paginated_responses(10, 100)
        call_count = 0

        def mock_response(_request):
            nonlocal call_count
            response = responses[min(call_count, len(responses) - 1)]
            call_count += 1
            return Response(200, json=response)

        mock_api.post("https://api.devrev.ai/accounts.list").mock(side_effect=mock_response)

        def fetch_all():
            nonlocal call_count
            call_count = 0
            all_accounts = []
            cursor = None

            for _ in range(10):  # Max 10 pages
                response = client.accounts.list(cursor=cursor, limit=100)
                all_accounts.extend(response.accounts)
                cursor = response.next_cursor
                if not cursor:
                    break

            return all_accounts

        benchmark(fetch_all)

    def test_memory_efficiency_large_dataset(self, benchmark, mock_api, client):
        """Benchmark memory efficiency with large dataset."""
        # Simulate 1000 items across 10 pages
        responses = create_paginated_responses(10, 100)
        call_count = 0

        def mock_response(_request):
            nonlocal call_count
            response = responses[min(call_count, len(responses) - 1)]
            call_count += 1
            return Response(200, json=response)

        mock_api.post("https://api.devrev.ai/accounts.list").mock(side_effect=mock_response)

        def process_pages():
            nonlocal call_count
            call_count = 0
            total = 0
            cursor = None

            for _ in range(10):
                response = client.accounts.list(cursor=cursor, limit=100)
                # Process each page without holding all in memory
                total += len(response.accounts)
                cursor = response.next_cursor
                if not cursor:
                    break

            return total

        benchmark(process_pages)
