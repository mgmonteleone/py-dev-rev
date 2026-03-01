# Services

API services provide access to DevRev resources.

## Overview

Services are accessed via the client:

```python
from devrev import DevRevClient

client = DevRevClient()

# Access services
client.accounts      # AccountsService
client.works         # WorksService
client.dev_users     # DevUsersService
# ... etc
```

## Available Services

### Core Resources

| Service | Description | Reference |
|---------|-------------|-----------|
| **Accounts** | Customer accounts | [accounts](accounts.md) |
| **Works** | Issues, tickets, tasks | [works](works.md) |
| **Dev Users** | Internal team members | [dev-users](dev-users.md) |
| **Rev Users** | External customers | [rev-users](rev-users.md) |
| **Parts** | Product components | [parts](parts.md) |

### Content & Communication

| Service | Description | Reference |
|---------|-------------|-----------|
| **Articles** | Knowledge base articles with unified content management | [articles](articles.md) |
| **Conversations** | Customer conversations | [conversations](conversations.md) |
| **Tags** | Categorization | [tags](tags.md) |
| **Timeline Entries** | Activity tracking | [timeline-entries](timeline-entries.md) |

### Collaboration

| Service | Description | Reference |
|---------|-------------|-----------|
| **Groups** | User groups | [groups](groups.md) |
| **Links** | Object relationships | [links](links.md) |

### Development

| Service | Description | Reference |
|---------|-------------|-----------|
| **Code Changes** | Code tracking | [code-changes](code-changes.md) |
| **Webhooks** | Event notifications | [webhooks](webhooks.md) |

### Operations

| Service | Description | Reference |
|---------|-------------|-----------|
| **SLAs** | Service level agreements | [slas](slas.md) |

## Common Patterns

### CRUD Operations

Most services support:

```python
# List resources
response = client.accounts.list(limit=10)

# Get single resource
response = client.accounts.get(id="ACC-123")

# Create resource
response = client.accounts.create(display_name="Acme")

# Update resource
response = client.accounts.update(id="ACC-123", ...)

# Delete resource
client.accounts.delete(id="ACC-123")
```

### Unified Article Management

The Articles service provides unified methods that automatically handle artifact storage:

```python
from devrev.models.articles import ArticleStatus

# Create article with content (3 lines vs 15+ with manual artifact handling)
article = client.articles.create_with_content(
    title="Getting Started",
    content="<h1>Welcome</h1><p>Guide content...</p>",
    owned_by=["don:identity:dvrv-us-1:devo/1:devu/1"],
)

# Get article with content
article_with_content = client.articles.get_with_content(article.id)
print(article_with_content.content)

# Update content
client.articles.update_content(
    id=article.id,
    content="<h1>Updated Content</h1>",
)
```

See the [Articles service documentation](articles.md) for detailed examples.

### Pagination

```python
cursor = None
while True:
    response = client.accounts.list(cursor=cursor, limit=100)
    for account in response.accounts:
        process(account)
    
    cursor = response.next_cursor
    if not cursor:
        break
```

### Async Services

All services have async equivalents:

```python
from devrev import AsyncDevRevClient

async with AsyncDevRevClient() as client:
    # Same API, but async
    response = await client.accounts.list()
```

