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

## Environment Variables

| Variable | Field | Default |
|----------|-------|---------|
| `DEVREV_API_TOKEN` | `api_token` | Required |
| `DEVREV_BASE_URL` | `base_url` | `https://api.devrev.ai` |
| `DEVREV_TIMEOUT` | `timeout` | `30` |
| `DEVREV_MAX_RETRIES` | `max_retries` | `3` |
| `DEVREV_LOG_LEVEL` | N/A | `WARN` |

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

