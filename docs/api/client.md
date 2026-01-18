# Client

The main entry points for using the DevRev SDK.

## DevRevClient

Synchronous client for blocking operations.

::: devrev.client.DevRevClient
    options:
      members:
        - __init__
        - accounts
        - works
        - dev_users
        - rev_users
        - parts
        - articles
        - conversations
        - tags
        - groups
        - webhooks
        - slas
        - timeline_entries
        - links
        - code_changes
        - close
        - __enter__
        - __exit__

## AsyncDevRevClient

Asynchronous client for async/await patterns.

::: devrev.client.AsyncDevRevClient
    options:
      members:
        - __init__
        - accounts
        - works
        - dev_users
        - rev_users
        - parts
        - articles
        - conversations
        - tags
        - groups
        - webhooks
        - slas
        - timeline_entries
        - links
        - code_changes
        - close
        - __aenter__
        - __aexit__

## Usage Examples

### Synchronous

```python
from devrev import DevRevClient

# Using context manager (recommended)
with DevRevClient() as client:
    accounts = client.accounts.list()

# Manual lifecycle
client = DevRevClient()
try:
    accounts = client.accounts.list()
finally:
    client.close()
```

### Asynchronous

```python
import asyncio
from devrev import AsyncDevRevClient

async def main():
    # Using async context manager (recommended)
    async with AsyncDevRevClient() as client:
        accounts = await client.accounts.list()

asyncio.run(main())
```

## Configuration

Both clients accept the same configuration:

```python
from devrev import DevRevClient, DevRevConfig, APIVersion

# Direct parameters
client = DevRevClient(
    api_token="your-token",
    base_url="https://api.devrev.ai",
    timeout=30,
)

# Config object
config = DevRevConfig(
    api_token="your-token",
    timeout=60,
    max_retries=5,
)
client = DevRevClient(config=config)
```

### API Version Selection

The SDK supports both Public (stable) and Beta (preview) APIs:

```python
from devrev import DevRevClient, APIVersion

# Use public API (default, stable)
client = DevRevClient()

# Use beta API (preview features)
client = DevRevClient(api_version=APIVersion.BETA)
```

When using the beta API, you gain access to additional services:

- Incidents - Production incident management
- Engagements - Customer engagement tracking
- Brands - Brand identity management
- UOMs - Units of measure for metrics
- Question Answers - Q&A knowledge base
- Recommendations - AI-powered recommendations
- Search - Advanced search capabilities

See [Beta API Overview](beta/index.md) for details.

See [Configuration Guide](../guides/configuration.md) for more configuration options.

