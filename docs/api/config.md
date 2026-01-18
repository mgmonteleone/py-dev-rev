# Configuration

Configuration classes for the DevRev SDK.

## DevRevConfig

::: devrev.config.DevRevConfig
    options:
      show_source: true
      members:
        - api_token
        - base_url
        - timeout
        - max_retries

## Helper Functions

### get_config

::: devrev.config.get_config
    options:
      show_source: true

### configure

::: devrev.config.configure
    options:
      show_source: true

## Usage

### Basic Configuration

```python
from devrev import DevRevConfig

config = DevRevConfig(
    api_token="your-api-token",
    base_url="https://api.devrev.ai",
    timeout=30,
    max_retries=3,
)
```

### From Environment

```python
from devrev import get_config

# Reads from environment variables
config = get_config()
```

### Global Configuration

```python
from devrev import configure, DevRevClient

# Set global configuration
configure(
    api_token="your-token",
    timeout=60,
)

# All new clients use this config
client = DevRevClient()
```

## APIVersion Enum

The SDK supports two API versions:

```python
from devrev import APIVersion

# Public API (default, stable)
APIVersion.PUBLIC  # "public"

# Beta API (preview features)
APIVersion.BETA    # "beta"
```

Use the beta API to access preview features:

```python
from devrev import DevRevClient, DevRevConfig, APIVersion

# Via client parameter
client = DevRevClient(api_version=APIVersion.BETA)

# Via config object
config = DevRevConfig(
    api_token="your-token",
    api_version=APIVersion.BETA,
)
client = DevRevClient(config=config)

# Via environment variable
# Set DEVREV_API_VERSION=beta
client = DevRevClient()  # Automatically uses beta
```

See [Beta API Overview](beta/index.md) for available beta services.

## Environment Variables

| Variable | Field | Default | Options |
|----------|-------|---------|---------|
| `DEVREV_API_TOKEN` | `api_token` | Required | Any valid token |
| `DEVREV_BASE_URL` | `base_url` | `https://api.devrev.ai` | Any HTTPS URL |
| `DEVREV_API_VERSION` | `api_version` | `public` | `public`, `beta` |
| `DEVREV_TIMEOUT` | `timeout` | `30` | 1-300 seconds |
| `DEVREV_MAX_RETRIES` | `max_retries` | `3` | 0-10 retries |
| `DEVREV_LOG_LEVEL` | `log_level` | `WARN` | `DEBUG`, `INFO`, `WARN`, `ERROR` |
| `DEVREV_LOG_FORMAT` | `log_format` | `text` | `text`, `json` |
| `DEVREV_MAX_CONNECTIONS` | `max_connections` | `100` | 1-1000 |
| `DEVREV_HTTP2` | `http2` | `false` | `true`, `false` |
| `DEVREV_CIRCUIT_BREAKER_ENABLED` | `circuit_breaker_enabled` | `true` | `true`, `false` |

## Validation

Configuration is validated using Pydantic:

```python
from devrev import DevRevConfig
from pydantic import ValidationError

try:
    config = DevRevConfig(api_token="")  # Empty token
except ValidationError as e:
    print(e)
```

See [Configuration Guide](../guides/configuration.md) for more details.

