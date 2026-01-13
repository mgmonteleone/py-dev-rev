# Rev Users Service

Manage external customers (rev users) in DevRev.

## RevUsersService

::: devrev.services.rev_users.RevUsersService
    options:
      show_source: true

## AsyncRevUsersService

::: devrev.services.rev_users.AsyncRevUsersService
    options:
      show_source: true

## Usage Examples

### List Rev Users

```python
from devrev import DevRevClient

client = DevRevClient()

response = client.rev_users.list(limit=20)
for user in response.rev_users:
    print(f"{user.display_name} ({user.email})")
```

### Get Rev User

```python
response = client.rev_users.get(id="don:identity:dvrv-us-1:devo/1:revu/123")
print(f"User: {response.rev_user.display_name}")
```

### Create Rev User

```python
response = client.rev_users.create(
    display_name="John Doe",
    email="john@example.com",
)
print(f"Created: {response.rev_user.id}")
```

