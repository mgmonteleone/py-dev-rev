# Testing

Learn how to test applications that use the DevRev SDK.

## Overview

The SDK uses `httpx` for HTTP requests, making it easy to mock with `respx` or similar libraries.

## Setting Up Tests

### Install Test Dependencies

```bash
pip install pytest pytest-asyncio respx
```

### Basic Test Structure

```python
import pytest
from devrev import DevRevClient

@pytest.fixture
def client():
    """Create a test client."""
    return DevRevClient(api_token="test-token")

def test_list_accounts(client, respx_mock):
    """Test listing accounts."""
    respx_mock.post("https://api.devrev.ai/accounts.list").respond(
        json={"accounts": [], "next_cursor": None}
    )
    
    response = client.accounts.list()
    assert response.accounts == []
```

## Mocking with respx

### Basic Mocking

```python
import respx
from httpx import Response
from devrev import DevRevClient

@respx.mock
def test_get_account():
    respx.post("https://api.devrev.ai/accounts.get").respond(
        json={
            "account": {
                "id": "ACC-123",
                "display_name": "Test Account",
                "created_date": "2026-01-01T00:00:00Z",
            }
        }
    )
    
    client = DevRevClient(api_token="test-token")
    response = client.accounts.get(id="ACC-123")
    
    assert response.account.id == "ACC-123"
    assert response.account.display_name == "Test Account"
```

### Mocking Errors

```python
import respx
from httpx import Response
from devrev import DevRevClient
from devrev.exceptions import NotFoundError

@respx.mock
def test_not_found():
    respx.post("https://api.devrev.ai/accounts.get").respond(
        status_code=404,
        json={"message": "Account not found"}
    )
    
    client = DevRevClient(api_token="test-token")
    
    with pytest.raises(NotFoundError):
        client.accounts.get(id="invalid")
```

### Mocking Rate Limits

```python
@respx.mock
def test_rate_limit():
    respx.post("https://api.devrev.ai/accounts.list").respond(
        status_code=429,
        headers={"Retry-After": "60"},
        json={"message": "Rate limit exceeded"}
    )
    
    client = DevRevClient(api_token="test-token")
    
    with pytest.raises(RateLimitError) as exc_info:
        client.accounts.list()
    
    assert exc_info.value.retry_after == 60
```

## Async Testing

```python
import pytest
import respx
from devrev import AsyncDevRevClient

@pytest.mark.asyncio
@respx.mock
async def test_async_list():
    respx.post("https://api.devrev.ai/accounts.list").respond(
        json={"accounts": [], "next_cursor": None}
    )
    
    async with AsyncDevRevClient(api_token="test-token") as client:
        response = await client.accounts.list()
        assert response.accounts == []
```

## Fixtures

### Reusable Mock Responses

```python
# conftest.py
import pytest
import respx

@pytest.fixture
def mock_accounts():
    """Mock account data."""
    return [
        {
            "id": "ACC-1",
            "display_name": "Account 1",
            "created_date": "2026-01-01T00:00:00Z",
        },
        {
            "id": "ACC-2", 
            "display_name": "Account 2",
            "created_date": "2026-01-02T00:00:00Z",
        },
    ]

@pytest.fixture
def mock_devrev(mock_accounts):
    """Set up mock DevRev API."""
    with respx.mock:
        respx.post("https://api.devrev.ai/accounts.list").respond(
            json={"accounts": mock_accounts, "next_cursor": None}
        )
        yield

def test_with_fixture(mock_devrev):
    client = DevRevClient(api_token="test-token")
    response = client.accounts.list()
    assert len(response.accounts) == 2
```

## Testing Patterns

### Test Request Bodies

```python
@respx.mock
def test_create_request():
    route = respx.post("https://api.devrev.ai/works.create").respond(
        json={"work": {"id": "WORK-1", "type": "ticket", "title": "Test"}}
    )
    
    client = DevRevClient(api_token="test-token")
    client.works.create(
        type="ticket",
        title="Bug Report",
        applies_to_part="PART-1"
    )
    
    # Verify request body
    assert route.called
    request_body = route.calls.last.request.content
    # Parse and verify as needed
```

### Test Pagination

```python
@respx.mock
def test_pagination():
    # First page
    respx.post("https://api.devrev.ai/accounts.list").respond(
        json={"accounts": [{"id": "ACC-1"}], "next_cursor": "cursor1"}
    )
    
    client = DevRevClient(api_token="test-token")
    response = client.accounts.list()
    
    assert len(response.accounts) == 1
    assert response.next_cursor == "cursor1"
```

## Best Practices

1. **Always mock external calls** - Never hit real APIs in unit tests
2. **Use fixtures** - Reuse mock data across tests
3. **Test error cases** - Verify error handling works correctly
4. **Test edge cases** - Empty responses, pagination, etc.
5. **Use `respx.mock` decorator** - Ensures mocks are cleaned up

## Integration Testing

For integration tests against a real API:

```python
import os
import pytest
from devrev import DevRevClient

@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("DEVREV_API_TOKEN"),
    reason="No API token"
)
def test_real_api():
    """Integration test against real API."""
    client = DevRevClient()
    response = client.accounts.list(limit=1)
    # Just verify it doesn't error
    assert response is not None
```

Run integration tests:

```bash
DEVREV_API_TOKEN=your-token pytest -m integration
```

## Next Steps

- [Error Handling](error-handling.md) - Test error scenarios
- [Examples](../examples/index.md) - See tested examples

