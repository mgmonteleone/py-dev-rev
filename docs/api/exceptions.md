# Exceptions

Exception classes for error handling in the DevRev SDK.

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
└── ConfigurationError
```

## Base Exception

### DevRevError

::: devrev.exceptions.DevRevError
    options:
      show_source: true
      members:
        - message
        - status_code
        - request_id

## HTTP Exceptions

### AuthenticationError

Raised when API authentication fails (HTTP 401).

::: devrev.exceptions.AuthenticationError

### ForbiddenError

Raised when access is denied (HTTP 403).

::: devrev.exceptions.ForbiddenError

### NotFoundError

Raised when a resource is not found (HTTP 404).

::: devrev.exceptions.NotFoundError

### ValidationError

Raised for invalid requests (HTTP 400).

::: devrev.exceptions.ValidationError

### ConflictError

Raised for resource conflicts (HTTP 409).

::: devrev.exceptions.ConflictError

### RateLimitError

Raised when rate limit is exceeded (HTTP 429).

::: devrev.exceptions.RateLimitError
    options:
      members:
        - retry_after

### ServerError

Raised for server errors (HTTP 500).

::: devrev.exceptions.ServerError

### ServiceUnavailableError

Raised when service is unavailable (HTTP 503).

::: devrev.exceptions.ServiceUnavailableError

## Client Exceptions

### TimeoutError

Raised when a request times out.

::: devrev.exceptions.TimeoutError

### NetworkError

Raised for network connectivity issues.

::: devrev.exceptions.NetworkError

### ConfigurationError

Raised for invalid SDK configuration.

::: devrev.exceptions.ConfigurationError

## Usage Examples

### Basic Error Handling

```python
from devrev import DevRevClient
from devrev.exceptions import DevRevError, NotFoundError

client = DevRevClient()

try:
    account = client.accounts.get(id="invalid")
except NotFoundError as e:
    print(f"Not found: {e.message}")
except DevRevError as e:
    print(f"API error: {e.message}")
```

### Rate Limit Handling

```python
import time
from devrev.exceptions import RateLimitError

try:
    response = client.accounts.list()
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
    time.sleep(e.retry_after)
    response = client.accounts.list()
```

### Comprehensive Handling

```python
from devrev.exceptions import (
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
    DevRevError,
)

try:
    client.works.create(...)
except AuthenticationError:
    print("Check your API token")
except ForbiddenError:
    print("You don't have permission")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except RateLimitError as e:
    print(f"Retry after {e.retry_after}s")
except ServerError as e:
    print(f"Server error (ID: {e.request_id})")
except DevRevError as e:
    print(f"Unexpected: {e.message}")
```

See [Error Handling Guide](../guides/error-handling.md) for more patterns.

