# Tags Service

Manage tags for categorization in DevRev.

## TagsService

::: devrev.services.tags.TagsService
    options:
      show_source: true

## AsyncTagsService

::: devrev.services.tags.AsyncTagsService
    options:
      show_source: true

## Usage Examples

### List Tags

```python
from devrev import DevRevClient

client = DevRevClient()

response = client.tags.list()
for tag in response.tags:
    print(f"{tag.name}")
```

### Create Tag

```python
response = client.tags.create(
    name="urgent",
    description="High priority items",
)
print(f"Created: {response.tag.id}")
```

