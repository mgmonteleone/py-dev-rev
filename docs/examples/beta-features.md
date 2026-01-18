# Beta API Features - Examples

This guide provides runnable examples for using DevRev Beta API features.

## Prerequisites

Enable the Beta API before running these examples:

```python
from devrev import DevRevClient, APIVersion

client = DevRevClient(api_version=APIVersion.BETA)
```

Or set the environment variable:

```bash
export DEVREV_API_VERSION=beta
export DEVREV_API_TOKEN=your-token-here
```

## Incident Management

Manage incidents with full lifecycle tracking, severity levels, and stage progression.

### Create and Track an Incident

```python
from devrev import DevRevClient, APIVersion
from devrev.models.incidents import IncidentSeverity, IncidentStage

client = DevRevClient(api_version=APIVersion.BETA)

# Create a new incident
incident = client.incidents.create(
    title="Database connection timeout in production",
    body="Users are experiencing 5-second delays when loading dashboards. "
         "Database connection pool appears to be exhausted.",
    severity=IncidentSeverity.SEV1,
    owned_by=["don:identity:dvrv-us-1:devo/1:devu/123"],
    applies_to_parts=["don:core:dvrv-us-1:devo/1:part/456"]
)

print(f"Created incident: {incident.id}")
print(f"Display ID: {incident.display_id}")
print(f"Severity: {incident.severity}")
```

### Update Incident Stages

```python
# Acknowledge the incident
incident = client.incidents.update(
    id=incident.id,
    stage=IncidentStage.ACKNOWLEDGED,
    body="Team notified. Investigating connection pool settings."
)

# Mark as identified
incident = client.incidents.update(
    id=incident.id,
    stage=IncidentStage.IDENTIFIED,
    body="Root cause: connection pool max size set to 10, should be 50."
)

# Mark as mitigated
incident = client.incidents.update(
    id=incident.id,
    stage=IncidentStage.MITIGATED,
    body="Increased pool size to 50. Monitoring performance."
)

# Resolve the incident
incident = client.incidents.update(
    id=incident.id,
    stage=IncidentStage.RESOLVED,
    body="Performance restored. No further timeouts observed."
)
```

### List and Filter Incidents

```python
# List all open incidents
open_incidents = client.incidents.list(
    stage=[IncidentStage.ACKNOWLEDGED, IncidentStage.IDENTIFIED],
    limit=20
)

for incident in open_incidents.incidents:
    print(f"{incident.display_id}: {incident.title} - {incident.stage}")

# List critical incidents
critical = client.incidents.list(
    severity=[IncidentSeverity.SEV0, IncidentSeverity.SEV1]
)

print(f"Found {len(critical.incidents)} critical incidents")
```

### Group Incidents by Severity

```python
# Group incidents by severity for reporting
groups = client.incidents.group(
    group_by="severity",
    limit=100
)

for group in groups:
    print(f"{group.key}: {group.count} incidents")
```

## Customer Engagement Tracking

Track customer interactions including calls, emails, and meetings.

### Create Customer Engagement

```python
from devrev import DevRevClient, APIVersion
from devrev.models.engagements import EngagementType
from datetime import datetime, timezone

client = DevRevClient(api_version=APIVersion.BETA)

# Log a customer call
engagement = client.engagements.create(
    title="Q1 Business Review Call",
    engagement_type=EngagementType.CALL,
    description="Discussed product roadmap, feature requests, and renewal timeline.",
    members=["don:identity:dvrv-us-1:devo/1:devu/123"],
    scheduled_date=datetime.now(timezone.utc),
    tags=["don:core:dvrv-us-1:devo/1:tag/customer-success"]
)

print(f"Logged engagement: {engagement.id}")
```

### Track Email Engagement

```python
# Log an email exchange
email_engagement = client.engagements.create(
    title="Feature Request Follow-up",
    engagement_type=EngagementType.EMAIL,
    description="Customer requested bulk export feature. Sent timeline and pricing.",
    members=["don:identity:dvrv-us-1:devo/1:devu/456"],
    tags=["don:core:dvrv-us-1:devo/1:tag/sales"]
)


### Core Search with Query Language

```python
# Use DevRev query language for precise filtering
results = client.search.core(
    query="type:ticket AND priority:p0 AND status:open",
    namespaces=[SearchNamespace.WORK],
    limit=20
)

for result in results.results:
    print(f"{result.id}: Score {result.score:.2f}")
```

### Search with Pagination

```python
# Paginate through search results
cursor = None
all_results = []

while True:
    results = client.search.hybrid(
        query="login problems",
        namespaces=[SearchNamespace.CONVERSATION],
        limit=50,
        cursor=cursor
    )

    all_results.extend(results.results)

    if not results.next_cursor:
        break
    cursor = results.next_cursor

print(f"Found {len(all_results)} total results")
```

## Async Examples

All beta features support async/await for high-performance applications.

### Async Incident Management

```python
import asyncio
from devrev import AsyncDevRevClient, APIVersion
from devrev.models.incidents import IncidentSeverity

async def manage_incidents():
    async with AsyncDevRevClient(api_version=APIVersion.BETA) as client:
        # Create incident
        incident = await client.incidents.create(
            title="API latency spike detected",
            severity=IncidentSeverity.SEV2,
            body="Response times increased by 300% in last 5 minutes"
        )

        # Get incident details
        details = await client.incidents.get(id=incident.id)
        print(f"Incident: {details.title}")

        # List all incidents concurrently
        sev1_task = client.incidents.list(severity=[IncidentSeverity.SEV1])
        sev2_task = client.incidents.list(severity=[IncidentSeverity.SEV2])

        sev1_incidents, sev2_incidents = await asyncio.gather(sev1_task, sev2_task)

        print(f"SEV1: {len(sev1_incidents.incidents)}, SEV2: {len(sev2_incidents.incidents)}")

asyncio.run(manage_incidents())
```

### Async Search

```python
import asyncio
from devrev import AsyncDevRevClient, APIVersion
from devrev.models.search import SearchNamespace

async def search_multiple():
    async with AsyncDevRevClient(api_version=APIVersion.BETA) as client:
        # Search multiple namespaces concurrently
        tasks = [
            client.search.hybrid("authentication", namespaces=[SearchNamespace.ARTICLE]),
            client.search.hybrid("authentication", namespaces=[SearchNamespace.CONVERSATION]),
            client.search.hybrid("authentication", namespaces=[SearchNamespace.WORK])
        ]

        results = await asyncio.gather(*tasks)

        for i, result in enumerate(results):
            print(f"Namespace {i}: {len(result.results)} results")

asyncio.run(search_multiple())
```

## Complete Example: Incident Response Workflow

Here's a complete example combining multiple beta features:

```python
from devrev import DevRevClient, APIVersion
from devrev.models.incidents import IncidentSeverity, IncidentStage
from devrev.models.engagements import EngagementType
from devrev.models.recommendations import ChatMessage, MessageRole, ChatCompletionRequest
from datetime import datetime, timezone

client = DevRevClient(api_version=APIVersion.BETA)

# 1. Create incident from customer report
incident = client.incidents.create(
    title="Payment processing failures",
    body="Multiple customers reporting failed credit card transactions",
    severity=IncidentSeverity.SEV0,
    owned_by=["don:identity:dvrv-us-1:devo/1:devu/123"]
)

print(f"Created incident: {incident.display_id}")

# 2. Search for similar past incidents
similar = client.search.hybrid(
    query="payment processing failures",
    namespaces=["work"],
    limit=5
)

print(f"Found {len(similar.results)} similar incidents")

# 3. Get AI recommendation for response
ai_request = ChatCompletionRequest(
    messages=[
        ChatMessage(role=MessageRole.SYSTEM, content="You are a technical support expert."),
        ChatMessage(role=MessageRole.USER, content=f"How should we respond to: {incident.body}")
    ],
    max_tokens=200
)

ai_response = client.recommendations.chat_completions(ai_request)
suggested_action = ai_response.choices[0].message.content

print(f"AI suggests: {suggested_action}")

# 4. Update incident with action plan
client.incidents.update(
    id=incident.id,
    stage=IncidentStage.ACKNOWLEDGED,
    body=f"Action plan: {suggested_action}"
)

# 5. Log customer communication
engagement = client.engagements.create(
    title=f"Customer notification - {incident.display_id}",
    engagement_type=EngagementType.EMAIL,
    description="Notified affected customers about payment issue and ETA for resolution",
    scheduled_date=datetime.now(timezone.utc)
)

print(f"Logged engagement: {engagement.id}")

# 6. Resolve incident
client.incidents.update(
    id=incident.id,
    stage=IncidentStage.RESOLVED,
    body="Payment gateway issue resolved. All transactions processing normally."
)

print("Incident resolved successfully")
```

## Error Handling

Always handle beta API errors gracefully:

```python
from devrev import DevRevClient, APIVersion
from devrev.exceptions import BetaAPIRequiredError, ValidationError, NotFoundError

client = DevRevClient(api_version=APIVersion.BETA)

try:
    incident = client.incidents.create(
        title="Test incident",
        severity="invalid_severity"  # This will fail validation
    )
except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Field errors: {e.field_errors}")
except BetaAPIRequiredError as e:
    print(f"Beta API required: {e.message}")
except NotFoundError as e:
    print(f"Resource not found: {e.message}")
```

## Next Steps

- Review the [Beta API Migration Guide](../guides/beta-api.md)
- Explore [API Differences Documentation](../api/beta-api-differences.md)
- Check out [Advanced Examples](./advanced.md) for more patterns

