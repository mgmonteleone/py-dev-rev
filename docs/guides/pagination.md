# Pagination

Learn how to efficiently iterate through large datasets with the DevRev SDK.

## Overview

The DevRev API uses cursor-based pagination. The SDK provides both manual cursor handling and convenient iterator patterns.

## Basic Pagination

### Manual Cursor Handling

```python
from devrev import DevRevClient

client = DevRevClient()

cursor = None
all_accounts = []

while True:
    response = client.accounts.list(cursor=cursor, limit=50)
    all_accounts.extend(response.accounts)
    
    # Check for more pages
    cursor = response.next_cursor
    if not cursor:
        break

print(f"Total accounts: {len(all_accounts)}")
```

### Limiting Results

```python
# Get only first 10 items
response = client.accounts.list(limit=10)

# Get specific page size
response = client.works.list(limit=25, cursor=some_cursor)
```

## Working with Large Datasets

### Processing in Batches

```python
def process_all_works():
    """Process all work items in batches."""
    client = DevRevClient()
    cursor = None
    processed = 0
    
    while True:
        response = client.works.list(cursor=cursor, limit=100)
        
        for work in response.works:
            process_work(work)  # Your processing logic
            processed += 1
        
        cursor = response.next_cursor
        if not cursor:
            break
        
        print(f"Processed {processed} items...")
    
    print(f"Done! Processed {processed} total items.")
```

### Async Pagination

```python
import asyncio
from devrev import AsyncDevRevClient

async def fetch_all_accounts():
    """Fetch all accounts asynchronously."""
    async with AsyncDevRevClient() as client:
        cursor = None
        all_accounts = []
        
        while True:
            response = await client.accounts.list(cursor=cursor, limit=100)
            all_accounts.extend(response.accounts)
            
            cursor = response.next_cursor
            if not cursor:
                break
        
        return all_accounts
```

## Filtering with Pagination

Combine filters with pagination:

```python
from devrev import DevRevClient
from devrev.models import WorkType

client = DevRevClient()

# Get all open tickets
cursor = None
open_tickets = []

while True:
    response = client.works.list(
        type=[WorkType.TICKET],
        stage_name=["open", "in_progress"],
        cursor=cursor,
        limit=50
    )
    open_tickets.extend(response.works)
    
    cursor = response.next_cursor
    if not cursor:
        break

print(f"Found {len(open_tickets)} open tickets")
```

## Export Operations

For bulk data export, use export endpoints:

```python
# Export up to 10,000 items
response = client.works.export(
    type=[WorkType.TICKET],
    first=10000
)

print(f"Exported {len(response.works)} work items")
```

## Best Practices

### 1. Use Appropriate Page Sizes

```python
# For processing: larger batches
response = client.works.list(limit=100)

# For UI display: smaller batches
response = client.accounts.list(limit=20)
```

### 2. Handle Rate Limits

```python
import time
from devrev.exceptions import RateLimitError

def paginate_with_retry(client):
    cursor = None
    
    while True:
        try:
            response = client.accounts.list(cursor=cursor, limit=50)
            yield from response.accounts
            
            cursor = response.next_cursor
            if not cursor:
                break
                
        except RateLimitError as e:
            print(f"Rate limited. Waiting {e.retry_after}s...")
            time.sleep(e.retry_after)
```

### 3. Memory Efficiency

Process items as you go instead of collecting all:

```python
def process_accounts_efficiently(client):
    """Process accounts without storing all in memory."""
    cursor = None
    
    while True:
        response = client.accounts.list(cursor=cursor, limit=100)
        
        for account in response.accounts:
            # Process immediately
            yield account
        
        cursor = response.next_cursor
        if not cursor:
            break

# Use as a generator
for account in process_accounts_efficiently(client):
    print(account.display_name)
```

### 4. Track Progress

```python
def paginate_with_progress(client, total_expected=None):
    """Show progress while paginating."""
    cursor = None
    count = 0
    
    while True:
        response = client.works.list(cursor=cursor, limit=100)
        
        for work in response.works:
            count += 1
            if total_expected:
                progress = count / total_expected * 100
                print(f"\rProgress: {progress:.1f}%", end="")
            yield work
        
        cursor = response.next_cursor
        if not cursor:
            break
    
    print(f"\nCompleted: {count} items")
```

## Common Patterns

### Count Then Fetch

```python
# First, get the count
count_response = client.works.count(type=[WorkType.ISSUE])
total = count_response.count
print(f"Total issues: {total}")

# Then paginate with progress
for i, work in enumerate(paginate_works(client)):
    print(f"Processing {i+1}/{total}: {work.title}")
```

### Parallel Page Fetching (Async)

```python
async def fetch_pages_parallel(client, page_count=5):
    """Fetch multiple pages in parallel."""
    first_response = await client.accounts.list(limit=100)
    
    # This is advanced - requires knowing cursor patterns
    # Generally, sequential pagination is recommended
```

## Next Steps

- [Error Handling](error-handling.md) - Handle pagination errors
- [Configuration](configuration.md) - Configure request timeouts
- [Testing](testing.md) - Mock paginated responses

