# Parts Service

Manage product parts and components in DevRev.

## PartsService

::: devrev.services.parts.PartsService
    options:
      show_source: true

## AsyncPartsService

::: devrev.services.parts.AsyncPartsService
    options:
      show_source: true

## Usage Examples

### List Parts

```python
from devrev import DevRevClient

client = DevRevClient()

response = client.parts.list(limit=20)
for part in response.parts:
    print(f"{part.name} ({part.type})")
```

### Get Part

```python
response = client.parts.get(id="don:core:dvrv-us-1:devo/1:part/123")
print(f"Part: {response.part.name}")
```

### Create Part

```python
response = client.parts.create(
    name="Authentication Module",
    type="capability",
    description="User authentication and authorization",
)
print(f"Created: {response.part.id}")
```

