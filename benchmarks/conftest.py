"""Shared fixtures for benchmarks."""

import pytest

# Sample data for benchmarks
SAMPLE_ACCOUNT_DATA = {
    "id": "don:identity:dvrv-us-1:devo/1:account/123",
    "display_name": "Acme Corporation",
    "domains": ["acme.com", "acme.io"],
    "created_date": "2024-01-15T10:30:00Z",
    "modified_date": "2024-06-20T14:45:00Z",
}

SAMPLE_WORK_DATA = {
    "id": "don:core:dvrv-us-1:devo/1:ticket/456",
    "display_id": "TKT-456",
    "type": "ticket",
    "title": "Customer cannot access dashboard",
    "body": "Customer reports 500 error when loading dashboard.",
    "created_date": "2024-06-15T09:00:00Z",
    "modified_date": "2024-06-20T14:45:00Z",
    "stage": {"name": "Open"},
    "severity": "high",
}

SAMPLE_USER_DATA = {
    "id": "don:identity:dvrv-us-1:devo/1:devu/789",
    "display_name": "John Developer",
    "email": "john@example.com",
    "created_date": "2024-01-01T00:00:00Z",
}


@pytest.fixture
def sample_account_data():
    """Return sample account data."""
    return SAMPLE_ACCOUNT_DATA.copy()


@pytest.fixture
def sample_work_data():
    """Return sample work data."""
    return SAMPLE_WORK_DATA.copy()


@pytest.fixture
def sample_user_data():
    """Return sample user data."""
    return SAMPLE_USER_DATA.copy()


@pytest.fixture
def many_accounts(sample_account_data):
    """Return a list of 100 account data dicts."""
    return [
        {**sample_account_data, "id": f"don:identity:dvrv-us-1:devo/1:account/{i}"}
        for i in range(100)
    ]


@pytest.fixture
def many_works(sample_work_data):
    """Return a list of 100 work data dicts."""
    return [{**sample_work_data, "id": f"don:core:dvrv-us-1:devo/1:ticket/{i}"} for i in range(100)]
