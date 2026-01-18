# Beta API Migration Guide

This guide helps you migrate from the DevRev Public API to the Beta API, which includes new features and services.

## Overview

The DevRev Beta API extends the Public API with:

- **7 new beta-only services** for advanced features
- **74 new endpoints** across incident management, engagement tracking, and AI-powered search
- **Enhanced existing services** with additional beta endpoints
- **Backwards compatible** - all public API features continue to work

## Enabling Beta API

There are three ways to enable the Beta API in your application:

### Method 1: Client Parameter (Recommended)

Pass `api_version` when creating the client:

```python
from devrev import DevRevClient, APIVersion

# Enable beta API
client = DevRevClient(api_version=APIVersion.BETA)

# Now you can access beta services
incidents = client.incidents.list()
```

### Method 2: Environment Variable

Set the `DEVREV_API_VERSION` environment variable:

```bash
export DEVREV_API_VERSION=beta
```

```python
from devrev import DevRevClient

# Automatically uses beta API from environment
client = DevRevClient()
```

### Method 3: Configuration Object

Use the `DevRevConfig` object:

```python
from devrev import DevRevClient, DevRevConfig, APIVersion

config = DevRevConfig(
    api_token="your-token",
    api_version=APIVersion.BETA
)

client = DevRevClient(config=config)
```

## Beta-Only Services

The following services are **only available** when using the Beta API:

| Service | Description | Key Features |
|---------|-------------|--------------|
| **incidents** | Incident management | Create, track, and resolve incidents with SLA integration |
| **engagements** | Customer engagement tracking | Track calls, emails, meetings, and customer interactions |
| **brands** | Brand management | Multi-brand support for organizations |
| **uoms** | Unit of Measurement | Metering and usage tracking with aggregation |
| **question_answers** | Q&A management | Manage question-answer pairs for knowledge base |
| **recommendations** | AI-powered recommendations | Chat completions and reply suggestions |
| **search** | Advanced search | Hybrid search combining keyword and semantic search |

### Additional Beta Services

- **preferences** - User preference management
- **notifications** - Notification management
- **track_events** - Event tracking and analytics

## Error Handling

When accessing beta-only features without enabling the Beta API, you'll receive a `BetaAPIRequiredError`:

```python
from devrev import DevRevClient, APIVersion
from devrev.exceptions import BetaAPIRequiredError

# Public API client (default)
client = DevRevClient(api_version=APIVersion.PUBLIC)

try:
    # This will raise BetaAPIRequiredError
    incidents = client.incidents.list()
except BetaAPIRequiredError as e:
    print(f"Error: {e.message}")
    print("Please enable beta API to use this feature")
```

### Handling the Error

```python
from devrev import DevRevClient, APIVersion
from devrev.exceptions import BetaAPIRequiredError

def get_incidents_safely(client):
    """Safely access incidents with fallback."""
    try:
        return client.incidents.list()
    except BetaAPIRequiredError:
        print("Incidents require beta API. Upgrade your client.")
        return None
```

## Best Practices

### 1. Feature Detection Pattern

Check if beta features are available before using them:

```python
from devrev import DevRevClient, APIVersion

def has_beta_features(client: DevRevClient) -> bool:
    """Check if client has beta API enabled."""
    return client._config.api_version == APIVersion.BETA

client = DevRevClient()

if has_beta_features(client):
    # Use beta features
    incidents = client.incidents.list()
else:
    # Fallback to public API features
    print("Beta features not available")
```

### 2. Gradual Migration

Migrate incrementally by enabling beta API only where needed:

```python
from devrev import DevRevClient, APIVersion

# Public API client for stable features
public_client = DevRevClient(api_version=APIVersion.PUBLIC)
accounts = public_client.accounts.list()

# Beta API client for new features
beta_client = DevRevClient(api_version=APIVersion.BETA)
incidents = beta_client.incidents.list()
```

### 3. Environment-Based Configuration

Use different API versions for different environments:

```python
# .env.development
DEVREV_API_VERSION=beta

# .env.production
DEVREV_API_VERSION=public
```

```python
from devrev import DevRevClient

# Automatically uses correct version per environment
client = DevRevClient()
```

### 4. Testing Beta Features

Test beta features thoroughly before production deployment:

```python
import pytest
from devrev import DevRevClient, APIVersion

@pytest.fixture
def beta_client():
    """Fixture for beta API testing."""
    return DevRevClient(api_version=APIVersion.BETA)

def test_incident_creation(beta_client):
    """Test incident creation with beta API."""
    incident = beta_client.incidents.create(
        title="Test Incident",
        severity="sev2"
    )
    assert incident.id is not None
```

## Migration Checklist

- [ ] Review beta-only services and identify features you need
- [ ] Update client initialization to enable beta API
- [ ] Test beta features in development environment
- [ ] Update error handling to catch `BetaAPIRequiredError`
- [ ] Update documentation and team training materials
- [ ] Deploy to staging and verify functionality
- [ ] Monitor for any API changes or deprecations
- [ ] Deploy to production

## Backwards Compatibility

The Beta API is **fully backwards compatible** with the Public API:

- All public API endpoints continue to work
- No breaking changes to existing functionality
- Beta features are additive only
- You can switch back to public API at any time

## Next Steps

- Explore [Beta Features Examples](../examples/beta-features.md)
- Review [API Differences Documentation](../api/beta-api-differences.md)
- Check the [Changelog](../changelog.md) for version history

