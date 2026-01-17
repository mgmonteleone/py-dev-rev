# Error Handling

Learn how to handle API errors gracefully with the DevRev SDK.

## Exception Hierarchy

```
DevRevError (base)
├── AuthenticationError (401)
├── ForbiddenError (403)
├── NotFoundError (404)
├── ValidationError (400)
├── ConflictError (409)
├── RateLimitError (429)
├── ServerError (500)
├── ServiceUnavailableError (503)
├── TimeoutError
├── NetworkError
├── CircuitBreakerError
└── ConfigurationError
```

## Basic Error Handling

```python
from devrev import DevRevClient
from devrev.exceptions import DevRevError, NotFoundError

client = DevRevClient()

try:
    work = client.works.get(id="invalid-id")
except NotFoundError as e:
    print(f"Work not found: {e.message}")
except DevRevError as e:
    print(f"API error: {e.message}")
```

## Handling Specific Errors

### Authentication Errors

```python
from devrev.exceptions import AuthenticationError

try:
    client = DevRevClient(api_token="invalid-token")
    client.accounts.list()
except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
    print("Check your API token and try again.")
```

### Not Found Errors

```python
from devrev.exceptions import NotFoundError

try:
    account = client.accounts.get(id="non-existent-id")
except NotFoundError as e:
    print(f"Account not found: {e.message}")
    # Create the account instead, or handle gracefully
```

### Validation Errors

```python
from devrev.exceptions import ValidationError

try:
    client.works.create(
        type="ticket",
        title="",  # Empty title - invalid!
        applies_to_part="don:core:..."
    )
except ValidationError as e:
    print(f"Invalid request: {e.message}")
    # e.field_errors may contain detailed field-level errors
```

### Rate Limit Errors

```python
import time
from devrev.exceptions import RateLimitError

try:
    response = client.accounts.list()
except RateLimitError as e:
    print(f"Rate limited! Retry after: {e.retry_after} seconds")
    time.sleep(e.retry_after)
    # Retry the request
    response = client.accounts.list()
```

### Server Errors

```python
from devrev.exceptions import ServerError, ServiceUnavailableError

try:
    response = client.accounts.list()
except ServiceUnavailableError:
    print("Service temporarily unavailable. Try again later.")
except ServerError as e:
    print(f"Server error: {e.message}")
    print(f"Request ID: {e.request_id}")  # Useful for support
```

### Circuit Breaker Errors

The circuit breaker pattern prevents cascading failures by temporarily blocking requests after repeated failures:

```python
from devrev.exceptions import CircuitBreakerError

try:
    response = client.accounts.list()
except CircuitBreakerError as e:
    print(f"Circuit breaker is open: {e.message}")
    print("Service is temporarily unavailable due to repeated failures")
    # Wait for recovery timeout before retrying
```

Check circuit breaker state:

```python
from devrev import DevRevClient

client = DevRevClient()

# Check if circuit is open
if client._http.is_circuit_open:
    print("Circuit breaker is open - requests will be blocked")
else:
    # Safe to make requests
    accounts = client.accounts.list()

# Get current circuit state
state = client._http.circuit_state
print(f"Circuit state: {state}")  # CLOSED, OPEN, or HALF_OPEN
```

## Error Properties

All exceptions include useful properties:

```python
from devrev.exceptions import DevRevError

try:
    client.accounts.get(id="invalid")
except DevRevError as e:
    print(f"Message: {e.message}")
    print(f"Status Code: {e.status_code}")
    print(f"Request ID: {e.request_id}")  # For DevRev support
```

## Retry Patterns

### Simple Retry with Backoff

```python
import time
from devrev.exceptions import DevRevError, RateLimitError

def retry_with_backoff(func, max_retries=3):
    """Retry a function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            wait_time = e.retry_after
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
        except DevRevError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            print(f"Error: {e.message}. Retrying in {wait_time}s...")
            time.sleep(wait_time)

# Usage
accounts = retry_with_backoff(lambda: client.accounts.list())
```

### Async Retry

```python
import asyncio
from devrev.exceptions import RateLimitError

async def retry_async(coro_func, max_retries=3):
    """Retry an async function with backoff."""
    for attempt in range(max_retries):
        try:
            return await coro_func()
        except RateLimitError as e:
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)

# Usage
accounts = await retry_async(lambda: client.accounts.list())
```

## Comprehensive Error Handling

```python
from devrev import DevRevClient
from devrev.exceptions import (
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
    DevRevError,
)

def safe_get_account(client, account_id):
    """Safely get an account with comprehensive error handling."""
    try:
        return client.accounts.get(id=account_id)
    
    except AuthenticationError:
        raise RuntimeError("Invalid API credentials")
    
    except ForbiddenError:
        raise PermissionError(f"No access to account {account_id}")
    
    except NotFoundError:
        return None  # Account doesn't exist
    
    except ValidationError as e:
        raise ValueError(f"Invalid account ID: {e.message}")
    
    except RateLimitError as e:
        raise RuntimeError(f"Rate limited. Retry after {e.retry_after}s")
    
    except ServerError as e:
        raise RuntimeError(f"Server error (ID: {e.request_id})")
    
    except DevRevError as e:
        raise RuntimeError(f"Unexpected error: {e.message}")
```

## Logging Errors

```python
import logging
from devrev.exceptions import DevRevError

logger = logging.getLogger(__name__)

try:
    client.accounts.list()
except DevRevError as e:
    logger.error(
        "DevRev API error",
        extra={
            "status_code": e.status_code,
            "message": e.message,
            "request_id": e.request_id,
        }
    )
```

## Next Steps

- [Logging](logging.md) - Configure logging for debugging
- [Configuration](configuration.md) - Configure retry behavior
- [Testing](testing.md) - Mock errors in tests

