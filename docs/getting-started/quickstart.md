# Quick Start

Get up and running with the DevRev Python SDK in under 5 minutes.

## Prerequisites

1. [Install the SDK](installation.md)
2. Have your DevRev API token ready

## Step 1: Set Up Authentication

Set your API token as an environment variable:

=== "Linux/macOS"

    ```bash
    export DEVREV_API_TOKEN="your-api-token-here"
    ```

=== "Windows (PowerShell)"

    ```powershell
    $env:DEVREV_API_TOKEN = "your-api-token-here"
    ```

=== "Windows (CMD)"

    ```cmd
    set DEVREV_API_TOKEN=your-api-token-here
    ```

Or create a `.env` file in your project:

```bash
# .env (never commit this file!)
DEVREV_API_TOKEN=your-api-token-here
```

## Step 2: Create a Client

```python
from devrev import DevRevClient

# The client automatically reads DEVREV_API_TOKEN from environment
client = DevRevClient()
```

## Step 3: Make Your First API Call

### List Accounts

```python
from devrev import DevRevClient

client = DevRevClient()

# List accounts
response = client.accounts.list(limit=5)

for account in response.accounts:
    print(f"Account: {account.display_name}")
    print(f"  ID: {account.id}")
    print(f"  Created: {account.created_date}")
    print()
```

### Get a Specific Work Item

```python
# Get a work item by ID
work = client.works.get(id="don:core:dvrv-us-1:devo/1:ticket/123")
print(f"Title: {work.work.title}")
print(f"Type: {work.work.type}")
print(f"Stage: {work.work.stage.name if work.work.stage else 'N/A'}")
```

### Create a Ticket

```python
from devrev.models import WorkType

# Create a new ticket
response = client.works.create(
    type=WorkType.TICKET,
    title="Customer cannot access dashboard",
    applies_to_part="don:core:dvrv-us-1:devo/1:part/1",
    body="Customer reports 500 error when loading the main dashboard."
)

print(f"Created ticket: {response.work.display_id}")
print(f"ID: {response.work.id}")
```

## Step 4: Use Async for Better Performance

For async applications:

```python
import asyncio
from devrev import AsyncDevRevClient

async def main():
    async with AsyncDevRevClient() as client:
        # All methods are async
        response = await client.accounts.list(limit=5)
        
        for account in response.accounts:
            print(f"{account.id}: {account.display_name}")

asyncio.run(main())
```

## Complete Example

Here's a complete script that demonstrates common operations:

```python
"""DevRev SDK Quick Start Example."""

from devrev import DevRevClient
from devrev.exceptions import DevRevError, NotFoundError

def main():
    # Initialize client
    client = DevRevClient()
    
    try:
        # List accounts
        print("=== Accounts ===")
        accounts = client.accounts.list(limit=3)
        for account in accounts.accounts:
            print(f"  • {account.display_name}")
        
        # List work items
        print("\n=== Recent Work Items ===")
        works = client.works.list(limit=5)
        for work in works.works:
            print(f"  • [{work.type}] {work.title}")
        
        # Handle specific work item
        if works.works:
            work_id = works.works[0].id
            detail = client.works.get(id=work_id)
            print(f"\n=== Work Detail ===")
            print(f"  Title: {detail.work.title}")
            print(f"  Type: {detail.work.type}")
            
    except NotFoundError as e:
        print(f"Not found: {e.message}")
    except DevRevError as e:
        print(f"API Error: {e.message}")

if __name__ == "__main__":
    main()
```

## What's Next?

<div class="grid cards" markdown>

-   :material-key: [**Authentication**](authentication.md)

    Learn about all authentication options

-   :material-book: [**Guides**](../guides/index.md)

    In-depth guides for common tasks

-   :material-api: [**API Reference**](../api/index.md)

    Complete API documentation

-   :material-code-tags: [**Examples**](../examples/index.md)

    Real-world example applications

</div>

