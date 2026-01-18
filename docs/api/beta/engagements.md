# Engagements Service

Track customer engagements including calls, meetings, emails, and other interactions.

!!! info "Beta API Only"
    This service is only available when using `APIVersion.BETA`. See [Beta API Overview](index.md) for setup instructions.

## EngagementsService

::: devrev.services.engagements.EngagementsService
    options:
      show_source: true
      members:
        - create
        - get
        - list
        - update
        - delete
        - count

## AsyncEngagementsService

::: devrev.services.engagements.AsyncEngagementsService
    options:
      show_source: true

## Usage Examples

### Create an Engagement

```python
from devrev import DevRevClient, APIVersion
from devrev.models.engagements import EngagementType
from datetime import datetime, timedelta

client = DevRevClient(api_version=APIVersion.BETA)

# Schedule a customer meeting
engagement = client.engagements.create(
    title="Q4 Business Review with Acme Corp",
    engagement_type=EngagementType.MEETING,
    description="Quarterly review of product usage and roadmap",
    members=["don:identity:dvrv-us-1:devo/1:devu/123"],
    scheduled_date=datetime.now() + timedelta(days=7),
    tags=["don:core:dvrv-us-1:devo/1:tag/456"],
)

print(f"Created engagement: {engagement.id}")
```

### List Engagements

```python
from devrev.models.engagements import EngagementType

# List all engagements
response = client.engagements.list()
for engagement in response.engagements:
    print(f"{engagement.title} ({engagement.engagement_type})")

# Filter by type and members
response = client.engagements.list(
    engagement_type=[EngagementType.CALL, EngagementType.MEETING],
    members=["don:identity:dvrv-us-1:devo/1:devu/123"],
    limit=20,
)
```

### Get an Engagement

```python
engagement = client.engagements.get(id="don:core:dvrv-us-1:devo/1:engagement/789")
print(f"Title: {engagement.title}")
print(f"Type: {engagement.engagement_type}")
print(f"Scheduled: {engagement.scheduled_date}")
```

### Update an Engagement

```python
from datetime import datetime, timedelta

# Reschedule a meeting
engagement = client.engagements.update(
    id="don:core:dvrv-us-1:devo/1:engagement/789",
    scheduled_date=datetime.now() + timedelta(days=14),
    description="Rescheduled due to customer request",
)
```

### Delete an Engagement

```python
client.engagements.delete(id="don:core:dvrv-us-1:devo/1:engagement/789")
```

### Count Engagements

```python
from devrev.models.engagements import EngagementType

# Count engagements by type
count = client.engagements.count(
    engagement_type=[EngagementType.CALL, EngagementType.MEETING]
)
print(f"Total calls and meetings: {count}")
```

### Async Usage

```python
import asyncio
from devrev import AsyncDevRevClient, APIVersion
from devrev.models.engagements import EngagementType

async def main():
    async with AsyncDevRevClient(api_version=APIVersion.BETA) as client:
        # Create engagement
        engagement = await client.engagements.create(
            title="Customer onboarding call",
            engagement_type=EngagementType.CALL,
        )
        
        # List engagements
        response = await client.engagements.list(limit=10)
        for engagement in response.engagements:
            print(engagement.title)

asyncio.run(main())
```

## Related Models

### Engagement

The main engagement model with all properties.

### EngagementType

Enum representing types of customer engagements:

- `CALL` - Phone call
- `CONVERSATION` - Chat or messaging conversation
- `CUSTOM` - Custom engagement type
- `DEFAULT` - Default engagement type
- `EMAIL` - Email communication
- `LINKED_IN` - LinkedIn interaction
- `MEETING` - In-person or virtual meeting
- `OFFLINE` - Offline interaction
- `SURVEY` - Customer survey

## Pagination

The `list()` method returns a paginated response:

```python
response = client.engagements.list(limit=50)

# Process first page
for engagement in response.engagements:
    print(engagement.title)

# Get next page if available
if response.next_cursor:
    next_response = client.engagements.list(
        cursor=response.next_cursor,
        limit=50,
    )
```

## Best Practices

1. **Choose the right type** - Use specific engagement types (CALL, MEETING, EMAIL) rather than DEFAULT
2. **Schedule in advance** - Set `scheduled_date` for future engagements
3. **Track participants** - Add all team members to the `members` list
4. **Link related engagements** - Use `parent` to create engagement hierarchies
5. **Tag appropriately** - Use tags to categorize engagements by account, product, or topic
6. **Add context** - Include detailed descriptions to help team members understand the engagement purpose

