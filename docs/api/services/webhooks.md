# Webhooks Service

Manage webhook configurations for event notifications.

## WebhooksService

::: devrev.services.webhooks.WebhooksService
    options:
      show_source: true

## AsyncWebhooksService

::: devrev.services.webhooks.AsyncWebhooksService
    options:
      show_source: true

## Usage Examples

### List Webhooks

```python
from devrev import DevRevClient

client = DevRevClient()

response = client.webhooks.list()
for webhook in response.webhooks:
    print(f"{webhook.url} - {webhook.status}")
```

### Create Webhook

```python
import os

response = client.webhooks.create(
    url="https://your-server.com/webhooks/devrev",
    event_types=["work.created", "work.updated"],
    secret=os.environ["WEBHOOK_SECRET"],  # Never hardcode!
)
print(f"Created: {response.webhook.id}")
```

### Update Webhook

```python
response = client.webhooks.update(
    id="don:integration:dvrv-us-1:devo/1:webhook/123",
    event_types=["work.created", "work.updated", "work.deleted"],
)
```

### Delete Webhook

```python
client.webhooks.delete(id="don:integration:dvrv-us-1:devo/1:webhook/123")
```

