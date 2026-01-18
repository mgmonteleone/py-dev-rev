# API Reference

Complete reference documentation for the DevRev Python SDK.

## Overview

The SDK is organized into:

- **Clients** - Entry points for API access
- **Services** - Grouped API endpoints by resource type
- **Models** - Pydantic models for requests and responses
- **Exceptions** - Error types for handling failures

## Clients

<div class="grid cards" markdown>

-   :material-sync: **DevRevClient**

    Synchronous client for blocking operations.

    [:octicons-arrow-right-24: Client Reference](client.md)

-   :material-lightning-bolt: **AsyncDevRevClient**

    Asynchronous client for async/await patterns.

    [:octicons-arrow-right-24: Client Reference](client.md)

</div>

## Services

All API operations are organized into service classes:

### Public API Services

| Service | Description | Endpoints |
|---------|-------------|-----------|
| [Accounts](services/accounts.md) | Customer account management | 7 |
| [Works](services/works.md) | Issues, tickets, tasks | 6 |
| [Dev Users](services/dev-users.md) | Internal team members | 10 |
| [Rev Users](services/rev-users.md) | External customers | 7 |
| [Parts](services/parts.md) | Product components | 5 |
| [Articles](services/articles.md) | Knowledge base | 5 |
| [Conversations](services/conversations.md) | Customer conversations | 5 |
| [Tags](services/tags.md) | Categorization | 5 |
| [Groups](services/groups.md) | User groups | 6 |
| [Webhooks](services/webhooks.md) | Event notifications | 6 |
| [SLAs](services/slas.md) | Service level agreements | 6 |
| [Timeline Entries](services/timeline-entries.md) | Activity tracking | 5 |
| [Links](services/links.md) | Object relationships | 5 |
| [Code Changes](services/code-changes.md) | Code tracking | 5 |

### Beta API Services

!!! info "Beta API Required"
    These services require `api_version=APIVersion.BETA`. See [Beta API Overview](beta/index.md).

| Service | Description | Documentation |
|---------|-------------|---------------|
| [Incidents](beta/incidents.md) | Production incident management | [View Docs](beta/incidents.md) |
| [Engagements](beta/engagements.md) | Customer engagement tracking | [View Docs](beta/engagements.md) |
| [Brands](beta/brands.md) | Brand identity management | [View Docs](beta/brands.md) |
| [UOMs](beta/uoms.md) | Units of measure for metrics | [View Docs](beta/uoms.md) |
| [Question Answers](beta/question-answers.md) | Q&A knowledge base | [View Docs](beta/question-answers.md) |
| [Recommendations](beta/recommendations.md) | AI-powered recommendations | [View Docs](beta/recommendations.md) |
| [Search](beta/search.md) | Advanced search capabilities | [View Docs](beta/search.md) |

[:octicons-arrow-right-24: Learn more about Beta API](beta/index.md)

## Models

Request and response models:

| Module | Description |
|--------|-------------|
| [Base](models/base.md) | Common base classes |
| [Accounts](models/accounts.md) | Account models |
| [Works](models/works.md) | Work item models |
| [Users](models/users.md) | User models |

## Exceptions

Error handling classes:

| Exception | HTTP Status | Description |
|-----------|-------------|-------------|
| `AuthenticationError` | 401 | Invalid credentials |
| `ForbiddenError` | 403 | Access denied |
| `NotFoundError` | 404 | Resource not found |
| `ValidationError` | 400 | Invalid request |
| `ConflictError` | 409 | Resource conflict |
| `RateLimitError` | 429 | Rate limit exceeded |
| `ServerError` | 500 | Server error |
| `ServiceUnavailableError` | 503 | Service unavailable |

[:octicons-arrow-right-24: Exceptions Reference](exceptions.md)

## Quick Usage

```python
from devrev import DevRevClient

# Initialize
client = DevRevClient()

# Access services
accounts = client.accounts.list()
works = client.works.create(...)
users = client.dev_users.get(id="...")
```

## Type Safety

All models are fully typed with Pydantic v2:

```python
from devrev.models import Work, WorkType

# IDE autocomplete works
work: Work = response.work
if work.type == WorkType.TICKET:
    print(work.severity)
```

