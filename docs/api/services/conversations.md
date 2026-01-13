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

