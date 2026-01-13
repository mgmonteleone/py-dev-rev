# Links Service

Manage object relationships and links in DevRev.

## LinksService

::: devrev.services.links.LinksService
    options:
      show_source: true

## AsyncLinksService

::: devrev.services.links.AsyncLinksService
    options:
      show_source: true

## Usage Examples

### List Links

```python
from devrev import DevRevClient

client = DevRevClient()

response = client.links.list(
    object="don:core:dvrv-us-1:devo/1:ticket/123"
)
for link in response.links:
    print(f"{link.link_type}: {link.target}")
```

### Create Link

```python
response = client.links.create(
    source="don:core:dvrv-us-1:devo/1:issue/123",
    target="don:core:dvrv-us-1:devo/1:ticket/456",
    link_type="is_blocked_by",
)
print(f"Created: {response.link.id}")
```

