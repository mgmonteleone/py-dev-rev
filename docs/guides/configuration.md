# Configuration

Configure the DevRev SDK for your environment and use case.

## Configuration Methods

### 1. Environment Variables (Recommended)

```bash
export DEVREV_API_TOKEN="your-api-token"
export DEVREV_BASE_URL="https://api.devrev.ai"
export DEVREV_TIMEOUT=30
export DEVREV_MAX_RETRIES=3
export DEVREV_LOG_LEVEL=INFO
```

### 2. Constructor Parameters

```python
from devrev import DevRevClient

client = DevRevClient(
    api_token="your-api-token",
    base_url="https://api.devrev.ai",
    timeout=30,
)
```

### 3. Configuration Object

```python
from devrev import DevRevClient, DevRevConfig

config = DevRevConfig(
    api_token="your-api-token",
    base_url="https://api.devrev.ai",
    timeout=60,
    max_retries=5,
)

client = DevRevClient(config=config)
```

## Configuration Options

| Option | Env Variable | Default | Description |
|--------|-------------|---------|-------------|
| `api_token` | `DEVREV_API_TOKEN` | Required | API authentication token |
| `base_url` | `DEVREV_BASE_URL` | `https://api.devrev.ai` | API base URL |
| `timeout` | `DEVREV_TIMEOUT` | `30` | Request timeout (seconds) |
| `max_retries` | `DEVREV_MAX_RETRIES` | `3` | Maximum retry attempts |
| `log_level` | `DEVREV_LOG_LEVEL` | `WARN` | Logging level |
| `log_format` | `DEVREV_LOG_FORMAT` | `text` | Log format (text, json) |
| `max_connections` | `DEVREV_MAX_CONNECTIONS` | `100` | Maximum connection pool size |
| `max_keepalive_connections` | `DEVREV_MAX_KEEPALIVE_CONNECTIONS` | `20` | Maximum keep-alive connections |
| `keepalive_expiry` | `DEVREV_KEEPALIVE_EXPIRY` | `30.0` | Keep-alive expiry (seconds) |
| `http2` | `DEVREV_HTTP2` | `false` | Enable HTTP/2 support |
| `circuit_breaker_enabled` | `DEVREV_CIRCUIT_BREAKER_ENABLED` | `true` | Enable circuit breaker |
| `circuit_breaker_threshold` | `DEVREV_CIRCUIT_BREAKER_THRESHOLD` | `5` | Failure threshold |
| `circuit_breaker_recovery_timeout` | `DEVREV_CIRCUIT_BREAKER_RECOVERY_TIMEOUT` | `30.0` | Recovery timeout (seconds) |

## Timeout Configuration

### Request Timeout

```python
# Short timeout for quick operations
client = DevRevClient(timeout=10)

# Longer timeout for bulk operations
config = DevRevConfig(timeout=120)
client = DevRevClient(config=config)
```

### Per-Request Timeout

```python
# The SDK uses a global timeout configured at client creation
# For operations needing different timeouts, create separate clients

quick_client = DevRevClient(timeout=5)
bulk_client = DevRevClient(timeout=300)
```

## Retry Configuration

### Default Behavior

The SDK automatically retries on:

- Rate limit errors (429)
- Server errors (500, 502, 503, 504)
- Network timeouts

### Custom Retry Count

```python
# More retries for unreliable networks
config = DevRevConfig(max_retries=5)

# No retries
config = DevRevConfig(max_retries=0)
```

## Environment-Specific Configuration

### Development

```bash
# .env.development
DEVREV_API_TOKEN=dev-token
DEVREV_TIMEOUT=60
DEVREV_LOG_LEVEL=DEBUG
```

### Production

```bash
# Production environment
DEVREV_API_TOKEN=prod-token
DEVREV_TIMEOUT=30
DEVREV_MAX_RETRIES=3
DEVREV_LOG_LEVEL=INFO
DEVREV_LOG_FORMAT=json
DEVREV_CIRCUIT_BREAKER_ENABLED=true
DEVREV_MAX_CONNECTIONS=100
DEVREV_HTTP2=false
```

### Testing

```python
from devrev import DevRevConfig

test_config = DevRevConfig(
    api_token="test-token",
    base_url="https://api-sandbox.devrev.ai",  # If available
    timeout=10,
    max_retries=1,
)
```

## Using .env Files

Create a `.env` file for local development:

```bash title=".env"
DEVREV_API_TOKEN=your-token-here
DEVREV_TIMEOUT=30
DEVREV_LOG_LEVEL=DEBUG
```

The SDK automatically loads `.env` files using `python-dotenv`.

!!! danger "Security"
    Never commit `.env` files to version control!
    ```gitignore
    # .gitignore
    .env
    .env.*
    !.env.sample
    ```

## Configuration Validation

Configuration is validated at client creation:

```python
from devrev import DevRevClient
from devrev.exceptions import ConfigurationError

try:
    client = DevRevClient(api_token="")  # Empty token
except ConfigurationError as e:
    print(f"Invalid config: {e.message}")
```

## Advanced Configuration

### Connection Pooling

Configure connection pool settings for optimal performance:

```python
from devrev import DevRevConfig

config = DevRevConfig(
    api_token="your-token",
    max_connections=100,  # Total connections
    max_keepalive_connections=20,  # Idle connections to keep alive
    keepalive_expiry=30.0,  # Seconds before closing idle connections
    http2=False,  # Enable HTTP/2 if needed
)
```

### Fine-Grained Timeouts

Use `TimeoutConfig` for granular timeout control:

```python
from devrev import DevRevClient, TimeoutConfig

# Custom timeout configuration
timeout_config = TimeoutConfig(
    connect=5.0,  # Connection timeout
    read=30.0,    # Read timeout
    write=30.0,   # Write timeout
    pool=10.0,    # Pool acquisition timeout
)

client = DevRevClient(timeout=timeout_config)
```

### Circuit Breaker Configuration

Configure circuit breaker for reliability:

```python
from devrev import DevRevConfig

config = DevRevConfig(
    api_token="your-token",
    circuit_breaker_enabled=True,
    circuit_breaker_threshold=5,  # Failures before opening
    circuit_breaker_recovery_timeout=30.0,  # Seconds before retry
    circuit_breaker_half_open_max_calls=3,  # Test calls in half-open state
)
```

### Production Logging

Enable JSON logging for production environments:

```python
from devrev import DevRevConfig

config = DevRevConfig(
    api_token="your-token",
    log_level="INFO",
    log_format="json",  # Structured JSON logs
)
```

### Proxy Configuration

Use environment variables:

```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=https://proxy.example.com:8080
```

## Configuration Precedence

When multiple sources provide the same setting:

1. Constructor parameters (highest priority)
2. Config object
3. Environment variables
4. Default values (lowest priority)

```python
# Environment: DEVREV_TIMEOUT=30

# Constructor wins
client = DevRevClient(timeout=60)  # Uses 60, not 30
```

## Best Practices

1. **Use environment variables** for tokens and secrets
2. **Use config objects** for programmatic configuration
3. **Create separate clients** for different use cases (e.g., different timeouts)
4. **Validate configuration** early in application startup
5. **Document required environment variables** for your team

## Next Steps

- [Authentication](../getting-started/authentication.md) - Token management
- [Logging](logging.md) - Configure logging
- [Testing](testing.md) - Test configuration

