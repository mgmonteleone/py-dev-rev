# Sync vs Async

The DevRev SDK provides both synchronous and asynchronous clients. This guide helps you choose the right one.

## Quick Comparison

| Feature | Synchronous | Asynchronous |
|---------|------------|--------------|
| **Client Class** | `DevRevClient` | `AsyncDevRevClient` |
| **Best For** | Scripts, CLI tools | Web apps, high concurrency |
| **Complexity** | Simple | Requires async/await |
| **Performance** | Good for sequential ops | Better for parallel ops |

## Synchronous Client

The simplest choice for most use cases.

### When to Use

- Scripts and CLI applications
- Simple integrations
- Low-volume API calls
- When you don't need concurrency

### Example

```python
from devrev import DevRevClient

client = DevRevClient()

# Simple, blocking calls
accounts = client.accounts.list(limit=10)
for account in accounts.accounts:
    print(account.display_name)

# Sequential operations
work = client.works.get(id="don:core:...")
client.works.update(id=work.work.id, title="Updated Title")
```

### Context Manager

Use context managers to ensure proper cleanup:

```python
with DevRevClient() as client:
    accounts = client.accounts.list()
    # Client is automatically closed when block exits
```

## Asynchronous Client

For high-performance and concurrent applications.

### When to Use

- Web applications (FastAPI, Starlette)
- High-volume API calls
- When making multiple independent requests
- When I/O performance is critical

### Example

```python
import asyncio
from devrev import AsyncDevRevClient

async def main():
    async with AsyncDevRevClient() as client:
        accounts = await client.accounts.list(limit=10)
        for account in accounts.accounts:
            print(account.display_name)

asyncio.run(main())
```

### Parallel Requests

The main advantage of async - concurrent requests:

```python
import asyncio
from devrev import AsyncDevRevClient

async def fetch_all():
    async with AsyncDevRevClient() as client:
        # Run multiple requests concurrently
        accounts_task = client.accounts.list()
        works_task = client.works.list(limit=10)
        users_task = client.dev_users.list()
        
        # Wait for all to complete
        accounts, works, users = await asyncio.gather(
            accounts_task,
            works_task,
            users_task
        )
        
        print(f"Accounts: {len(accounts.accounts)}")
        print(f"Works: {len(works.works)}")
        print(f"Users: {len(users.dev_users)}")

asyncio.run(fetch_all())
```

## Framework Integration

### FastAPI

```python
from fastapi import FastAPI, Depends
from devrev import AsyncDevRevClient

app = FastAPI()

async def get_devrev_client():
    async with AsyncDevRevClient() as client:
        yield client

@app.get("/accounts")
async def list_accounts(client: AsyncDevRevClient = Depends(get_devrev_client)):
    response = await client.accounts.list(limit=10)
    return {"accounts": [a.display_name for a in response.accounts]}
```

### Flask

```python
from flask import Flask
from devrev import DevRevClient

app = Flask(__name__)

@app.route("/accounts")
def list_accounts():
    with DevRevClient() as client:
        response = client.accounts.list(limit=10)
        return {"accounts": [a.display_name for a in response.accounts]}
```

## Performance Comparison

### Sequential Sync Requests

```python
# ~3 seconds for 3 requests (1s each)
accounts = client.accounts.list()
works = client.works.list()
users = client.dev_users.list()
```

### Concurrent Async Requests

```python
# ~1 second for 3 requests (parallel)
accounts, works, users = await asyncio.gather(
    client.accounts.list(),
    client.works.list(),
    client.dev_users.list()
)
```

## Migration Tips

### Converting Sync to Async

1. Change `DevRevClient` to `AsyncDevRevClient`
2. Add `async` to function definitions
3. Add `await` to API calls
4. Use `asyncio.run()` for the entry point

```python
# Before (sync)
def get_accounts():
    client = DevRevClient()
    return client.accounts.list()

# After (async)
async def get_accounts():
    async with AsyncDevRevClient() as client:
        return await client.accounts.list()

# Run it
asyncio.run(get_accounts())
```

## Best Practices

1. **Use context managers** - Ensures proper resource cleanup
2. **Don't mix clients** - Choose one pattern per application
3. **Use async for web apps** - Better scalability
4. **Use sync for scripts** - Simpler code
5. **Limit concurrency** - Don't overwhelm the API with too many parallel requests

## Next Steps

- [Pagination](pagination.md) - Handle large datasets
- [Error Handling](error-handling.md) - Handle async errors
- [Examples](../examples/index.md) - See both patterns in action

