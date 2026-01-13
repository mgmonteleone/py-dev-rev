# Groups Service

Manage user groups in DevRev.

## GroupsService

::: devrev.services.groups.GroupsService
    options:
      show_source: true

## AsyncGroupsService

::: devrev.services.groups.AsyncGroupsService
    options:
      show_source: true

## Usage Examples

### List Groups

```python
from devrev import DevRevClient

client = DevRevClient()

response = client.groups.list()
for group in response.groups:
    print(f"{group.name}")
```

### Create Group

```python
response = client.groups.create(
    name="Support Team",
    description="Customer support agents",
)
print(f"Created: {response.group.id}")
```

