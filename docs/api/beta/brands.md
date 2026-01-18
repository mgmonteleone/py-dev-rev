# Brands Service

Manage brand identities, logos, and visual assets for your organization.

!!! info "Beta API Only"
    This service is only available when using `APIVersion.BETA`. See [Beta API Overview](index.md) for setup instructions.

## BrandsService

::: devrev.services.brands.BrandsService
    options:
      show_source: true
      members:
        - create
        - get
        - list
        - update
        - delete

## AsyncBrandsService

::: devrev.services.brands.AsyncBrandsService
    options:
      show_source: true

## Usage Examples

### Create a Brand

```python
from devrev import DevRevClient, APIVersion

client = DevRevClient(api_version=APIVersion.BETA)

brand = client.brands.create(
    name="Acme Corporation",
    description="Primary corporate brand",
    logo_url="https://example.com/logos/acme-logo.png",
)

print(f"Created brand: {brand.id}")
print(f"Name: {brand.name}")
```

### List Brands

```python
# List all brands
response = client.brands.list()
for brand in response.brands:
    print(f"{brand.name}: {brand.logo_url}")

# With pagination
response = client.brands.list(limit=10)
```

### Get a Brand

```python
brand = client.brands.get(id="don:core:dvrv-us-1:devo/1:brand/123")
print(f"Name: {brand.name}")
print(f"Description: {brand.description}")
print(f"Logo: {brand.logo_url}")
```

### Update a Brand

```python
# Update brand details
brand = client.brands.update(
    id="don:core:dvrv-us-1:devo/1:brand/123",
    name="Acme Corp",
    description="Updated brand description",
    logo_url="https://example.com/logos/acme-new-logo.png",
)
```

### Delete a Brand

```python
client.brands.delete(id="don:core:dvrv-us-1:devo/1:brand/123")
```

### Async Usage

```python
import asyncio
from devrev import AsyncDevRevClient, APIVersion

async def main():
    async with AsyncDevRevClient(api_version=APIVersion.BETA) as client:
        # Create brand
        brand = await client.brands.create(
            name="DevRev",
            description="DevRev platform brand",
        )
        
        # List brands
        response = await client.brands.list()
        for brand in response.brands:
            print(brand.name)

asyncio.run(main())
```

## Related Models

### Brand

The main brand model with properties:

- `id` - Unique brand identifier
- `name` - Brand name
- `description` - Brand description
- `logo_url` - URL to brand logo image
- `created_date` - When the brand was created
- `modified_date` - When the brand was last updated

## Pagination

The `list()` method returns a paginated response:

```python
response = client.brands.list(limit=50)

# Process first page
for brand in response.brands:
    print(brand.name)

# Get next page if available
if response.next_cursor:
    next_response = client.brands.list(
        cursor=response.next_cursor,
        limit=50,
    )
```

## Best Practices

1. **Use descriptive names** - Choose clear, recognizable brand names
2. **Host logos externally** - Store logo images on a CDN or asset server
3. **Maintain consistency** - Keep brand information up-to-date across all systems
4. **Document usage** - Use the description field to note where the brand is used
5. **Version control** - When updating logos, consider versioning in the URL

## Common Use Cases

### Multi-Brand Organizations

```python
# Create brands for different product lines
enterprise_brand = client.brands.create(
    name="Acme Enterprise",
    description="Enterprise product line",
    logo_url="https://cdn.example.com/acme-enterprise.png",
)

consumer_brand = client.brands.create(
    name="Acme Consumer",
    description="Consumer product line",
    logo_url="https://cdn.example.com/acme-consumer.png",
)
```

### White-Label Solutions

```python
# Create customer-specific brands
customer_brand = client.brands.create(
    name="Customer Co (Powered by Acme)",
    description="White-label brand for Customer Co",
    logo_url="https://cdn.example.com/customer-co-logo.png",
)
```

