# Conversations Service

Manage customer conversations in DevRev.

## ConversationsService

::: devrev.services.conversations.ConversationsService
    options:
      show_source: true

## AsyncConversationsService

::: devrev.services.conversations.AsyncConversationsService
    options:
      show_source: true

## Usage Examples

### List Conversations

```python
from devrev import DevRevClient

client = DevRevClient()

response = client.conversations.list(limit=20)
for conv in response.conversations:
    print(f"{conv.id}: {conv.title}")
```

### Get Conversation

```python
response = client.conversations.get(id="don:core:dvrv-us-1:devo/1:conversation/123")
print(f"Title: {response.conversation.title}")
```

### Sort Order

`list` accepts a `sort_by` parameter. Both forms are accepted and normalized
to the server form before the request is sent:

- Canonical: `"modified_date:desc"`, `"created_date:asc"`
- Legacy shortcut: `"-modified_date"` (descending), `"created_date"` (ascending)

!!! note "Server requires `field:direction`"
    The DevRev server rejects bare `"-field"` entries. The SDK normalizes
    legacy shortcuts to the `field:direction` form on your behalf.

### List Conversations Modified Since

Use `list_modified_since` to stream conversations that changed within a recent
window. It pages server-side sorted `modified_date:desc` and stops as soon as
a record older than the cutoff is seen.

```python
from datetime import datetime, timedelta, timezone
from devrev import DevRevClient

client = DevRevClient()

cutoff = datetime.now(timezone.utc) - timedelta(days=7)
recent = client.conversations.list_modified_since(cutoff, limit=200)
for conv in recent:
    print(f"{conv.id}: {conv.title}")
```

### Async Usage

```python
import asyncio
from datetime import datetime, timedelta, timezone
from devrev import AsyncDevRevClient

async def main():
    async with AsyncDevRevClient() as client:
        cutoff = datetime.now(timezone.utc) - timedelta(days=1)
        recent = await client.conversations.list_modified_since(cutoff)
        for conv in recent:
            print(f"{conv.id}: {conv.title}")

asyncio.run(main())
```

