# Account Models

Models for customer account operations.

## Account

The main account model.

::: devrev.models.accounts.Account
    options:
      show_source: true

## Request Models

### AccountsListRequest

::: devrev.models.accounts.AccountsListRequest
    options:
      show_source: true

### AccountsGetRequest

::: devrev.models.accounts.AccountsGetRequest
    options:
      show_source: true

### AccountsCreateRequest

::: devrev.models.accounts.AccountsCreateRequest
    options:
      show_source: true

### AccountsUpdateRequest

::: devrev.models.accounts.AccountsUpdateRequest
    options:
      show_source: true

### AccountsDeleteRequest

::: devrev.models.accounts.AccountsDeleteRequest
    options:
      show_source: true

## Response Models

### AccountsListResponse

::: devrev.models.accounts.AccountsListResponse
    options:
      show_source: true

### AccountsGetResponse

::: devrev.models.accounts.AccountsGetResponse
    options:
      show_source: true

### AccountsCreateResponse

::: devrev.models.accounts.AccountsCreateResponse
    options:
      show_source: true

## Usage Examples

### Create Account Request

```python
from devrev.models import AccountsCreateRequest

request = AccountsCreateRequest(
    display_name="Acme Corporation",
    domains=["acme.com"],
    description="Enterprise customer",
)
```

### Work with Account Response

```python
response = client.accounts.get(id="...")
account = response.account

print(f"Name: {account.display_name}")
print(f"ID: {account.id}")
print(f"Created: {account.created_date}")
print(f"Domains: {account.domains}")
```

