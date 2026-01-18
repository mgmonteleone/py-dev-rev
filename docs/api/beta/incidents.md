# Incidents Service

Manage production incidents with severity tracking and lifecycle management.

!!! info "Beta API Only"
    This service is only available when using `APIVersion.BETA`. See [Beta API Overview](index.md) for setup instructions.

## IncidentsService

::: devrev.services.incidents.IncidentsService
    options:
      show_source: true
      members:
        - create
        - get
        - list
        - update
        - delete
        - group

## AsyncIncidentsService

::: devrev.services.incidents.AsyncIncidentsService
    options:
      show_source: true

## Usage Examples

### Create an Incident

```python
from devrev import DevRevClient, APIVersion
from devrev.models.incidents import IncidentSeverity

client = DevRevClient(api_version=APIVersion.BETA)

incident = client.incidents.create(
    title="Database connection pool exhausted",
    body="Production database experiencing connection timeouts",
    severity=IncidentSeverity.SEV1,
    owned_by=["don:identity:dvrv-us-1:devo/1:devu/123"],
    applies_to_parts=["don:core:dvrv-us-1:devo/1:product/456"],
)

print(f"Created incident: {incident.id}")
print(f"Display ID: {incident.display_id}")
```

### List Incidents

```python
from devrev.models.incidents import IncidentStage, IncidentSeverity

# List all incidents
response = client.incidents.list()
for incident in response.incidents:
    print(f"{incident.display_id}: {incident.title}")

# Filter by stage and severity
response = client.incidents.list(
    stage=[IncidentStage.ACKNOWLEDGED, IncidentStage.IDENTIFIED],
    severity=[IncidentSeverity.SEV0, IncidentSeverity.SEV1],
    limit=20,
)
```

### Get an Incident

```python
incident = client.incidents.get(id="don:core:dvrv-us-1:devo/1:incident/789")
print(f"Title: {incident.title}")
print(f"Stage: {incident.stage}")
print(f"Severity: {incident.severity}")
```

### Update an Incident

```python
from devrev.models.incidents import IncidentStage

# Update incident stage
incident = client.incidents.update(
    id="don:core:dvrv-us-1:devo/1:incident/789",
    stage=IncidentStage.MITIGATED,
    body="Database connection pool increased from 100 to 200",
)
```

### Delete an Incident

```python
client.incidents.delete(id="don:core:dvrv-us-1:devo/1:incident/789")
```

### Group Incidents

```python
# Group incidents by severity
groups = client.incidents.group(
    group_by="severity",
    limit=10,
)

for group in groups:
    print(f"{group.key}: {group.count} incidents")
```

### Async Usage

```python
import asyncio
from devrev import AsyncDevRevClient, APIVersion
from devrev.models.incidents import IncidentSeverity

async def main():
    async with AsyncDevRevClient(api_version=APIVersion.BETA) as client:
        # Create incident
        incident = await client.incidents.create(
            title="API latency spike",
            severity=IncidentSeverity.SEV2,
        )
        
        # List incidents
        response = await client.incidents.list(limit=10)
        for incident in response.incidents:
            print(incident.title)

asyncio.run(main())
```

## Related Models

### Incident

The main incident model with all properties.

### IncidentStage

Enum representing incident lifecycle stages:

- `ACKNOWLEDGED` - Incident has been acknowledged
- `IDENTIFIED` - Root cause identified
- `MITIGATED` - Impact has been mitigated
- `RESOLVED` - Incident fully resolved

### IncidentSeverity

Enum representing incident severity levels:

- `SEV0` - Critical, complete outage
- `SEV1` - High, major functionality impaired
- `SEV2` - Medium, partial functionality impaired
- `SEV3` - Low, minor issues

## Pagination

The `list()` method returns a paginated response:

```python
response = client.incidents.list(limit=50)

# Process first page
for incident in response.incidents:
    print(incident.title)

# Get next page if available
if response.next_cursor:
    next_response = client.incidents.list(
        cursor=response.next_cursor,
        limit=50,
    )
```

## Best Practices

1. **Set appropriate severity** - Use SEV0/SEV1 for production-impacting incidents
2. **Track ownership** - Always assign incidents to responsible team members
3. **Update stages** - Keep incident stage current as you progress through resolution
4. **Link to parts** - Associate incidents with affected product components
5. **Document resolution** - Update the body with resolution details before closing

