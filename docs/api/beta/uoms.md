# UOMs Service

Define and manage Units of Measure (UOMs) for tracking metrics and analytics.

!!! info "Beta API Only"
    This service is only available when using `APIVersion.BETA`. See [Beta API Overview](index.md) for setup instructions.

## UomsService

::: devrev.services.uoms.UomsService
    options:
      show_source: true
      members:
        - create
        - get
        - list
        - update
        - delete
        - count

## AsyncUomsService

::: devrev.services.uoms.AsyncUomsService
    options:
      show_source: true

## Usage Examples

### Create a UOM

```python
from devrev import DevRevClient, APIVersion
from devrev.models.uoms import UomAggregationType, UomMetricScope

client = DevRevClient(api_version=APIVersion.BETA)

# Create a UOM for tracking API calls
uom = client.uoms.create(
    name="API Calls",
    aggregation_type=UomAggregationType.SUM,
    description="Total number of API calls made",
    metric_scope=UomMetricScope.ORG,
    dimensions=["endpoint", "status_code"],
    is_enabled=True,
)

print(f"Created UOM: {uom.id}")
```

### List UOMs

```python
from devrev.models.uoms import UomAggregationType

# List all UOMs
response = client.uoms.list()
for uom in response.uoms:
    print(f"{uom.name}: {uom.aggregation_type}")

# Filter by aggregation type
response = client.uoms.list(
    aggregation_type=[UomAggregationType.SUM, UomAggregationType.UNIQUE_COUNT],
    is_enabled=True,
    limit=20,
)
```

### Get a UOM

```python
uom = client.uoms.get(id="don:core:dvrv-us-1:devo/1:uom/123")
print(f"Name: {uom.name}")
print(f"Aggregation: {uom.aggregation_type}")
print(f"Dimensions: {uom.dimensions}")
```

### Update a UOM

```python
# Update UOM details
uom = client.uoms.update(
    id="don:core:dvrv-us-1:devo/1:uom/123",
    name="API Calls (Updated)",
    description="Updated description",
    is_enabled=False,
)
```

### Delete a UOM

```python
client.uoms.delete(id="don:core:dvrv-us-1:devo/1:uom/123")
```

### Count UOMs

```python
from devrev.models.uoms import UomAggregationType

# Count enabled UOMs
count = client.uoms.count(is_enabled=True)
print(f"Total enabled UOMs: {count}")

# Count by aggregation type
count = client.uoms.count(
    aggregation_type=[UomAggregationType.SUM]
)
print(f"Sum-based UOMs: {count}")
```

### Async Usage

```python
import asyncio
from devrev import AsyncDevRevClient, APIVersion
from devrev.models.uoms import UomAggregationType, UomMetricScope

async def main():
    async with AsyncDevRevClient(api_version=APIVersion.BETA) as client:
        # Create UOM
        uom = await client.uoms.create(
            name="Active Users",
            aggregation_type=UomAggregationType.UNIQUE_COUNT,
            metric_scope=UomMetricScope.ORG,
        )
        
        # List UOMs
        response = await client.uoms.list(limit=10)
        for uom in response.uoms:
            print(uom.name)

asyncio.run(main())
```

## Related Models

### Uom

The main UOM model with properties:

- `id` - Unique UOM identifier
- `name` - UOM name
- `description` - UOM description
- `aggregation_type` - How values are aggregated
- `metric_scope` - Organization or user-level metrics
- `dimensions` - Metric dimensions for grouping
- `is_enabled` - Whether the UOM is active

### UomAggregationType

Enum representing how metric values are aggregated:

- `SUM` - Sum all values
- `MINIMUM` - Take minimum value
- `MAXIMUM` - Take maximum value
- `UNIQUE_COUNT` - Count unique values
- `RUNNING_TOTAL` - Cumulative total over time
- `DURATION` - Time duration
- `LATEST` - Most recent value
- `OLDEST` - Oldest value

### UomMetricScope

Enum representing metric scope:

- `ORG` - Organization-wide metrics
- `USER` - Per-user metrics

## Pagination

The `list()` method returns a paginated response:

```python
response = client.uoms.list(limit=50)

# Process first page
for uom in response.uoms:
    print(uom.name)

# Get next page if available
if response.next_cursor:
    next_response = client.uoms.list(
        cursor=response.next_cursor,
        limit=50,
    )
```

## Best Practices

1. **Choose appropriate aggregation** - Select the aggregation type that matches your metric's nature
2. **Define dimensions** - Use dimensions to enable detailed breakdowns and filtering
3. **Set metric scope** - Choose ORG for company-wide metrics, USER for per-user tracking
4. **Enable/disable carefully** - Disable UOMs that are no longer needed rather than deleting them
5. **Document thoroughly** - Use clear names and descriptions for easy understanding

