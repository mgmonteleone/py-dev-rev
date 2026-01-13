# Basic Examples

Simple examples for common DevRev SDK operations.

## List Accounts

```python
"""List all customer accounts."""
from devrev import DevRevClient

def main():
    client = DevRevClient()
    
    response = client.accounts.list(limit=20)
    
    print(f"Found {len(response.accounts)} accounts:\n")
    for account in response.accounts:
        print(f"  • {account.display_name}")
        print(f"    ID: {account.id}")
        if account.domains:
            print(f"    Domains: {', '.join(account.domains)}")
        print()

if __name__ == "__main__":
    main()
```

## Create Work Items

### Create a Ticket

```python
"""Create a customer support ticket."""
from devrev import DevRevClient
from devrev.models import WorkType, TicketSeverity

def create_ticket():
    client = DevRevClient()
    
    response = client.works.create(
        type=WorkType.TICKET,
        title="Customer cannot access dashboard",
        applies_to_part="don:core:dvrv-us-1:devo/1:part/1",
        body="""
Customer reports 500 error when loading dashboard.

Steps to reproduce:
1. Log in as customer
2. Click on Dashboard
3. See error message

Expected: Dashboard loads
Actual: 500 Internal Server Error
        """,
        severity=TicketSeverity.HIGH,
    )
    
    print(f"Created ticket: {response.work.display_id}")
    print(f"ID: {response.work.id}")

if __name__ == "__main__":
    create_ticket()
```

### Create an Issue

```python
"""Create an engineering issue."""
from devrev import DevRevClient
from devrev.models import WorkType, IssuePriority

def create_issue():
    client = DevRevClient()
    
    response = client.works.create(
        type=WorkType.ISSUE,
        title="Implement dark mode support",
        applies_to_part="don:core:dvrv-us-1:devo/1:part/1",
        body="Add dark mode toggle to user preferences.",
        priority=IssuePriority.P2,
    )
    
    print(f"Created issue: {response.work.display_id}")

if __name__ == "__main__":
    create_issue()
```

## Pagination

```python
"""Iterate through all work items with pagination."""
from devrev import DevRevClient

def list_all_works():
    client = DevRevClient()
    
    cursor = None
    total = 0
    
    while True:
        response = client.works.list(cursor=cursor, limit=100)
        
        for work in response.works:
            total += 1
            print(f"{total}. [{work.type}] {work.title}")
        
        cursor = response.next_cursor
        if not cursor:
            break
    
    print(f"\nTotal: {total} work items")

if __name__ == "__main__":
    list_all_works()
```

## Error Handling

```python
"""Demonstrate error handling."""
from devrev import DevRevClient
from devrev.exceptions import (
    NotFoundError,
    ValidationError,
    RateLimitError,
    DevRevError,
)

def safe_get_work(work_id: str):
    client = DevRevClient()
    
    try:
        response = client.works.get(id=work_id)
        print(f"Found: {response.work.title}")
        return response.work
    
    except NotFoundError:
        print(f"Work item {work_id} not found")
        return None
    
    except ValidationError as e:
        print(f"Invalid ID: {e.message}")
        return None
    
    except RateLimitError as e:
        print(f"Rate limited. Retry after {e.retry_after}s")
        return None
    
    except DevRevError as e:
        print(f"API error: {e.message}")
        return None

if __name__ == "__main__":
    safe_get_work("don:core:dvrv-us-1:devo/1:ticket/123")
```

## Async Example

```python
"""Async client usage example."""
import asyncio
from devrev import AsyncDevRevClient

async def main():
    async with AsyncDevRevClient() as client:
        # List accounts
        accounts = await client.accounts.list(limit=5)
        print(f"Accounts: {len(accounts.accounts)}")
        
        # List works
        works = await client.works.list(limit=5)
        print(f"Works: {len(works.works)}")
        
        # Concurrent requests
        results = await asyncio.gather(
            client.dev_users.list(limit=5),
            client.tags.list(),
        )
        print(f"Users: {len(results[0].dev_users)}")
        print(f"Tags: {len(results[1].tags)}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Search Users

```python
"""Search for users."""
from devrev import DevRevClient

def search_users():
    client = DevRevClient()
    
    # List dev users
    print("Dev Users:")
    response = client.dev_users.list(limit=10)
    for user in response.dev_users:
        print(f"  • {user.display_name} ({user.email})")
    
    # List rev users
    print("\nRev Users:")
    response = client.rev_users.list(limit=10)
    for user in response.rev_users:
        print(f"  • {user.display_name}")

if __name__ == "__main__":
    search_users()
```

