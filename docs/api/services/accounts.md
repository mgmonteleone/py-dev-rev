# Accounts Service

Manage customer accounts in DevRev.

## AccountsService

::: devrev.services.accounts.AccountsService
    options:
      show_source: true
      members:
        - list
        - get
        - create
        - update
        - delete
        - export

## AsyncAccountsService

::: devrev.services.accounts.AsyncAccountsService
    options:
      show_source: true

## Usage Examples

### List Accounts

```python
from devrev import DevRevClient

client = DevRevClient()

# List all accounts
response = client.accounts.list()
for account in response.accounts:
    print(f"{account.id}: {account.display_name}")

# With filters
response = client.accounts.list(
    limit=10,
    # Add filters as supported by the API
)
```

### Get Account

```python
response = client.accounts.get(id="don:core:dvrv-us-1:devo/1:account/123")
print(f"Account: {response.account.display_name}")
print(f"Created: {response.account.created_date}")
```

### Create Account

```python
response = client.accounts.create(
    display_name="Acme Corporation",
    domains=["acme.com", "acme.io"],
    description="Major enterprise customer",
)
print(f"Created: {response.account.id}")
```

### Update Account

```python
response = client.accounts.update(
    id="don:core:dvrv-us-1:devo/1:account/123",
    display_name="Acme Corp (Updated)",
    description="Updated description",
)
```

### Delete Account

```python
client.accounts.delete(id="don:core:dvrv-us-1:devo/1:account/123")
```

### Export Accounts

```python
response = client.accounts.export(first=1000)
print(f"Exported {len(response.accounts)} accounts")
```

### Async Usage

```python
import asyncio
from devrev import AsyncDevRevClient

async def main():
    async with AsyncDevRevClient() as client:
        response = await client.accounts.list(limit=10)
        for account in response.accounts:
            print(account.display_name)

asyncio.run(main())
```

## Related Models

- [`Account`](../models/accounts.md#account)
- [`AccountsListRequest`](../models/accounts.md#accountslistrequest)
- [`AccountsCreateRequest`](../models/accounts.md#accountscreaterequest)

