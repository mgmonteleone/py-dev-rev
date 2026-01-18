# DevRev SDK Usage Guidelines

This rule file provides guidance for AI agents when generating code that uses the DevRev Python SDK.

## Client Initialization

### Environment Variables (Recommended)

Always use environment variables for API tokens - never hardcode:

```python
# Correct - reads from DEVREV_API_TOKEN environment variable
from devrev import DevRevClient

client = DevRevClient()
```

### Context Managers

Always use context managers for proper resource cleanup:

```python
# Sync client
with DevRevClient() as client:
    accounts = client.accounts.list()

# Async client
async with AsyncDevRevClient() as client:
    accounts = await client.accounts.list()
```

### Configuration

For custom configuration:

```python
from devrev import DevRevClient, DevRevConfig

config = DevRevConfig(
    api_token=os.environ["DEVREV_API_TOKEN"],
    timeout=60,
    max_retries=3
)
client = DevRevClient(config=config)
```

## Response Handling

Response objects contain data in nested attributes - always access the correct attribute:

```python
# CORRECT
accounts_response = client.accounts.list()
for account in accounts_response.accounts:  # Note: .accounts
    print(account.display_name)

# CORRECT
work_response = client.works.get(id="don:core:...")
print(work_response.work.title)  # Note: .work

# INCORRECT - This will fail
# print(accounts_response.title)  # Wrong! Response is not the data
```

## Error Handling

Always handle exceptions from `devrev.exceptions`:

```python
from devrev.exceptions import (
    DevRevError,
    NotFoundError,
    ValidationError,
    RateLimitError,
)

try:
    work = client.works.get(id=work_id)
except NotFoundError:
    # Handle missing resource
    pass
except RateLimitError as e:
    # Wait and retry
    time.sleep(e.retry_after)
except DevRevError as e:
    # Log error details
    logger.error(f"API error: {e.message}, status: {e.status_code}")
```

## Pagination

DevRev uses cursor-based pagination - never use page numbers:

```python
# CORRECT - cursor-based pagination
cursor = None
all_items = []

while True:
    response = client.accounts.list(cursor=cursor, limit=50)
    all_items.extend(response.accounts)
    cursor = response.next_cursor
    if not cursor:
        break
```

## Creating Work Items

Always use the `WorkType` enum and provide required fields:

```python
from devrev.models import WorkType

# Creating a ticket (customer-facing)
response = client.works.create(
    type=WorkType.TICKET,
    title="Descriptive title",
    applies_to_part="don:core:dvrv-us-1:devo/1:part/1",  # Required
    body="Detailed description"
)

# Creating an issue (internal)
response = client.works.create(
    type=WorkType.ISSUE,
    title="Bug: Dashboard loading error",
    applies_to_part="don:core:dvrv-us-1:devo/1:part/1",
    body="Technical details..."
)
```

## ID Format

DevRev uses DON (DevRev Object Notation) IDs:

```
don:core:dvrv-us-1:devo/1:ticket/123
don:core:dvrv-us-1:devo/1:part/456
don:identity:dvrv-us-1:devo/1:devu/789
```

Never construct IDs manually - always use IDs returned from API responses.

## Async Best Practices

For concurrent operations, use `asyncio.gather`:

```python
import asyncio
from devrev import AsyncDevRevClient

async def fetch_data():
    async with AsyncDevRevClient() as client:
        # Parallel requests - much faster
        accounts, works, users = await asyncio.gather(
            client.accounts.list(limit=10),
            client.works.list(limit=50),
            client.dev_users.list()
        )
        return accounts, works, users
```

## Anti-Patterns to Avoid

1. **Never hardcode API tokens** in source code
2. **Never use page numbers** - use cursor-based pagination
3. **Never access response data directly** - use the nested attribute
4. **Never create clients without cleanup** - use context managers
5. **Never ignore rate limits** - handle `RateLimitError` with retry
6. **Never construct DON IDs** - always use IDs from API responses

## Beta API

For beta features, explicitly enable the beta API:

```python
from devrev import DevRevClient, APIVersion

client = DevRevClient(api_version=APIVersion.BETA)
# Now beta services are available: incidents, engagements, search, etc.
```

