# Advanced Examples

Complex patterns and best practices for the DevRev SDK.

## Concurrent Requests

```python
"""Execute multiple API calls concurrently."""
import asyncio
from devrev import AsyncDevRevClient

async def fetch_dashboard_data():
    """Fetch all data needed for a dashboard in parallel."""
    async with AsyncDevRevClient() as client:
        # Run all requests concurrently
        accounts, works, users = await asyncio.gather(
            client.accounts.list(limit=10),
            client.works.list(limit=50),
            client.dev_users.list(limit=20),
        )
        
        return {
            "accounts": len(accounts.accounts),
            "works": len(works.works),
            "users": len(users.dev_users),
        }

async def main():
    data = await fetch_dashboard_data()
    print(f"Dashboard Data:")
    for key, value in data.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Retry with Backoff

```python
"""Implement custom retry logic with exponential backoff."""
import time
from devrev import DevRevClient
from devrev.exceptions import RateLimitError, ServerError, DevRevError

def retry_with_backoff(func, max_retries=5, base_delay=1):
    """Execute a function with exponential backoff on failure."""
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            wait_time = e.retry_after or (base_delay * (2 ** attempt))
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
        except ServerError:
            wait_time = base_delay * (2 ** attempt)
            print(f"Server error. Retrying in {wait_time}s...")
            time.sleep(wait_time)
        except DevRevError:
            if attempt == max_retries - 1:
                raise
            time.sleep(base_delay)
    
    raise RuntimeError("Max retries exceeded")

def main():
    client = DevRevClient()
    
    # Use retry wrapper
    response = retry_with_backoff(
        lambda: client.accounts.list(limit=100)
    )
    print(f"Fetched {len(response.accounts)} accounts")

if __name__ == "__main__":
    main()
```

## Webhook Handler

```python
"""Handle DevRev webhooks."""
import hashlib
import hmac
import json
from typing import Any

class WebhookHandler:
    def __init__(self, secret: str):
        self.secret = secret
        self.handlers = {}
    
    def on(self, event_type: str):
        """Decorator to register event handlers."""
        def decorator(func):
            self.handlers[event_type] = func
            return func
        return decorator
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature."""
        expected = hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)
    
    def process(self, payload: bytes, signature: str) -> Any:
        """Process incoming webhook."""
        if not self.verify_signature(payload, signature):
            raise ValueError("Invalid signature")
        
        data = json.loads(payload)
        event_type = data.get("type")
        
        handler = self.handlers.get(event_type)
        if handler:
            return handler(data)
        
        return None

# Usage example
webhook = WebhookHandler(secret="your-webhook-secret")

@webhook.on("work.created")
def handle_work_created(data):
    print(f"New work item: {data['work']['title']}")

@webhook.on("work.updated")
def handle_work_updated(data):
    print(f"Work updated: {data['work']['id']}")
```

## Data Export

```python
"""Export large datasets efficiently."""
import json
from datetime import datetime
from pathlib import Path
from devrev import DevRevClient

def export_all_works(output_dir: str = "exports"):
    """Export all work items to JSON files."""
    client = DevRevClient()
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export using the export endpoint for large datasets
    response = client.works.export(first=10000)
    
    filename = output_path / f"works_{timestamp}.json"
    with open(filename, "w") as f:
        works_data = [w.model_dump() for w in response.works]
        json.dump(works_data, f, indent=2, default=str)
    
    print(f"Exported {len(response.works)} works to {filename}")
    return filename

if __name__ == "__main__":
    export_all_works()
```

## Batch Operations

```python
"""Process items in batches."""
import asyncio
from devrev import AsyncDevRevClient

async def process_in_batches(items: list, batch_size: int = 10):
    """Process items in batches with concurrency control."""
    async with AsyncDevRevClient() as client:
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # Process batch concurrently
            tasks = [
                client.works.get(id=item_id)
                for item_id in batch
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for item_id, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"Error processing {item_id}: {result}")
                else:
                    print(f"Processed: {result.work.title}")
            
            # Small delay between batches
            await asyncio.sleep(0.1)
```

## Custom Logging

```python
"""Configure custom logging for debugging."""
import logging
from devrev import DevRevClient

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Set devrev logger to debug
logging.getLogger("devrev").setLevel(logging.DEBUG)

def main():
    client = DevRevClient()
    
    # All API calls will be logged
    response = client.accounts.list(limit=5)
    print(f"Found {len(response.accounts)} accounts")

if __name__ == "__main__":
    main()
```

