# Dev Users Service

Manage internal team members (developers, support agents) in DevRev.

## DevUsersService

::: devrev.services.dev_users.DevUsersService
    options:
      show_source: true

## AsyncDevUsersService

::: devrev.services.dev_users.AsyncDevUsersService
    options:
      show_source: true

## Usage Examples

### List Dev Users

```python
from devrev import DevRevClient

client = DevRevClient()

response = client.dev_users.list(limit=20)
for user in response.dev_users:
    print(f"{user.display_name} ({user.email})")
```

### Get Dev User

```python
response = client.dev_users.get(id="don:identity:dvrv-us-1:devo/1:devu/123")
print(f"User: {response.dev_user.display_name}")
print(f"Email: {response.dev_user.email}")
```

### Async Usage

```python
async with AsyncDevRevClient() as client:
    response = await client.dev_users.list()
    for user in response.dev_users:
        print(user.display_name)
```

