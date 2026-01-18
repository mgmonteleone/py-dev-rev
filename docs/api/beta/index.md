# Beta API Overview

The DevRev Python SDK supports both **Public** (stable) and **Beta** (preview) APIs. Beta APIs provide access to new features and services that are still under development and may change.

!!! warning "Beta Stability Notice"
    Beta APIs are subject to change without notice. Features may be modified, renamed, or removed in future releases. Use beta APIs in production with caution and be prepared to update your code when changes occur.

## Enabling Beta API

There are three ways to enable the beta API:

### 1. Client Parameter (Recommended)

Pass `api_version` when creating the client:

```python
from devrev import DevRevClient, APIVersion

# Enable beta API
client = DevRevClient(api_version=APIVersion.BETA)

# Now you can access beta services
incidents = client.incidents.list()
search_results = client.search.core("type:ticket")
```

### 2. Environment Variable

Set the `DEVREV_API_VERSION` environment variable:

```bash
export DEVREV_API_VERSION=beta
```

```python
from devrev import DevRevClient

# Automatically uses beta API from environment
client = DevRevClient()
```

### 3. Configuration Object

Use a `DevRevConfig` object:

```python
from devrev import DevRevClient, DevRevConfig, APIVersion

config = DevRevConfig(
    api_token="your-token",
    api_version=APIVersion.BETA
)

client = DevRevClient(config=config)
```

## Available Beta Services

The following services are **only available** when using the beta API:

| Service | Description | Documentation |
|---------|-------------|---------------|
| [Incidents](incidents.md) | Manage production incidents with severity tracking | [View Docs](incidents.md) |
| [Engagements](engagements.md) | Track customer engagements (calls, meetings, emails) | [View Docs](engagements.md) |
| [Brands](brands.md) | Manage brand identities and logos | [View Docs](brands.md) |
| [UOMs](uoms.md) | Define units of measure for metrics | [View Docs](uoms.md) |
| [Question Answers](question-answers.md) | Manage Q&A knowledge base | [View Docs](question-answers.md) |
| [Recommendations](recommendations.md) | AI-powered chat completions and reply suggestions | [View Docs](recommendations.md) |
| [Search](search.md) | Advanced search with core and hybrid modes | [View Docs](search.md) |

## Beta vs Public API

### Public API (Default)
- Stable, production-ready endpoints
- Backward compatibility guaranteed
- Recommended for production use
- Services: accounts, works, users, articles, conversations, etc.

### Beta API
- Preview of new features
- May change without notice
- Early access to cutting-edge capabilities
- All public services **plus** beta-only services

## Async Support

All beta services support async operations:

```python
import asyncio
from devrev import AsyncDevRevClient, APIVersion

async def main():
    async with AsyncDevRevClient(api_version=APIVersion.BETA) as client:
        # Use beta services asynchronously
        incidents = await client.incidents.list()
        results = await client.search.hybrid("authentication issues")

asyncio.run(main())
```

## Migration Guide

When a beta feature becomes stable, it will be promoted to the public API. You'll need to:

1. Update your code to use the public API version
2. Check for any API changes in the release notes
3. Test thoroughly before deploying

## Getting Help

- **Documentation**: See individual service pages for detailed usage
- **Issues**: Report bugs or request features on GitHub
- **Support**: Contact DevRev support for production issues

## Next Steps

Explore the beta services:

- [Incidents Service](incidents.md) - Production incident management
- [Search Service](search.md) - Advanced search capabilities
- [Recommendations Service](recommendations.md) - AI-powered features

