# Logging & Debugging

Configure logging to debug issues and monitor SDK behavior.

## Log Levels

Set the log level via environment variable:

```bash
export DEVREV_LOG_LEVEL=DEBUG  # DEBUG, INFO, WARN, ERROR
```

| Level | Description |
|-------|-------------|
| `DEBUG` | Detailed request/response information |
| `INFO` | General operational information |
| `WARN` | Warning messages (default) |
| `ERROR` | Error messages only |

## Basic Configuration

### Using Environment Variables

```bash
# Enable debug logging
export DEVREV_LOG_LEVEL=DEBUG
```

```python
from devrev import DevRevClient

# Logging is automatically configured
client = DevRevClient()
client.accounts.list()  # Logs will appear
```

### Programmatic Configuration

```python
import logging

# Configure the devrev logger
logging.getLogger("devrev").setLevel(logging.DEBUG)

# Add a handler if needed
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
))
logging.getLogger("devrev").addHandler(handler)
```

## Log Output Examples

### DEBUG Level

```
2026-01-13 10:30:45 [DEBUG] devrev.http: POST /accounts.list
2026-01-13 10:30:45 [DEBUG] devrev.http: Headers: {'Content-Type': 'application/json'}
2026-01-13 10:30:46 [DEBUG] devrev.http: Response 200 (245ms)
```

### INFO Level

```
2026-01-13 10:30:45 [INFO] devrev.client: Initialized DevRevClient
2026-01-13 10:30:46 [INFO] devrev.http: Request completed (245ms)
```

### WARN Level

```
2026-01-13 10:30:47 [WARN] devrev.http: Rate limit approaching (80% used)
2026-01-13 10:30:48 [WARN] devrev.http: Retry attempt 1/3 after error
```

## Custom Logger Integration

Use your application's logger:

```python
import logging

# Set up your application logger
app_logger = logging.getLogger("myapp")
app_logger.setLevel(logging.INFO)

# Configure devrev to use a child logger
devrev_logger = logging.getLogger("myapp.devrev")
devrev_logger.setLevel(logging.DEBUG)

# Logs will flow to your application's handlers
```

## Structured Logging

For production environments with log aggregation:

```python
import json
import logging

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        return json.dumps(log_data)

# Apply to devrev logger
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.getLogger("devrev").addHandler(handler)
```

## Debugging Tips

### Debug Specific Requests

```python
import logging

# Enable debug for just one operation
logger = logging.getLogger("devrev")
original_level = logger.level
logger.setLevel(logging.DEBUG)

try:
    result = client.accounts.list()
finally:
    logger.setLevel(original_level)
```

### Log Request/Response Bodies

!!! warning "Security Warning"
    Only use in development! May expose sensitive data.

```python
import httpx

def log_request(request):
    print(f"Request: {request.method} {request.url}")
    print(f"Body: {request.content}")

def log_response(response):
    print(f"Response: {response.status_code}")
    print(f"Body: {response.text[:500]}")  # Truncate

# Note: This requires custom HTTP client configuration
```

### Check Request IDs

Every response includes a request ID for debugging:

```python
from devrev.exceptions import DevRevError

try:
    client.accounts.get(id="invalid")
except DevRevError as e:
    print(f"Request ID: {e.request_id}")
    # Use this ID when contacting DevRev support
```

## Production Logging

### Recommended Settings

```bash
# Production
export DEVREV_LOG_LEVEL=WARN

# Staging
export DEVREV_LOG_LEVEL=INFO

# Development
export DEVREV_LOG_LEVEL=DEBUG
```

### Security Considerations

The SDK is designed to never log:

- API tokens or credentials
- Full request/response bodies at INFO level
- Sensitive headers

```python
# Safe to use in production
logging.getLogger("devrev").setLevel(logging.INFO)
```

## Integration with Observability Tools

### OpenTelemetry

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("devrev_operation"):
    accounts = client.accounts.list()
```

### Sentry

```python
import sentry_sdk
from devrev.exceptions import DevRevError

sentry_sdk.init(dsn="your-sentry-dsn")

try:
    client.accounts.list()
except DevRevError as e:
    sentry_sdk.capture_exception(e)
```

## Next Steps

- [Error Handling](error-handling.md) - Handle logged errors
- [Configuration](configuration.md) - Other SDK options
- [Testing](testing.md) - Test with logging

