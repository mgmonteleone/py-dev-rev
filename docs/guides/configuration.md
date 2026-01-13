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
| - | `DEVREV_LOG_LEVEL` | `WARN` | Logging level |

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
DEVREV_LOG_LEVEL=WARN
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

### Custom HTTP Settings

```python
from devrev import DevRevConfig

config = DevRevConfig(
    api_token="your-token",
    timeout=30,
    max_retries=3,
    # Additional HTTP settings are handled internally
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

