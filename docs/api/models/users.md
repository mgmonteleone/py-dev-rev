# User Models

Models for dev users (internal) and rev users (external).

## Dev User Models

### DevUser

::: devrev.models.dev_users.DevUser
    options:
      show_source: true

### DevUsersListRequest

::: devrev.models.dev_users.DevUsersListRequest
    options:
      show_source: true

### DevUsersListResponse

::: devrev.models.dev_users.DevUsersListResponse
    options:
      show_source: true

## Rev User Models

### RevUser

::: devrev.models.rev_users.RevUser
    options:
      show_source: true

### RevUsersListRequest

::: devrev.models.rev_users.RevUsersListRequest
    options:
      show_source: true

### RevUsersListResponse

::: devrev.models.rev_users.RevUsersListResponse
    options:
      show_source: true

## Usage Examples

### Working with Dev Users

```python
response = client.dev_users.list(limit=10)
for user in response.dev_users:
    print(f"{user.display_name} ({user.email})")
```

### Working with Rev Users

```python
response = client.rev_users.list(limit=10)
for user in response.rev_users:
    print(f"{user.display_name}")
```

