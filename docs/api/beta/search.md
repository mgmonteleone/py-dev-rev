# Search Service

Advanced search capabilities with core query language and hybrid semantic search.

!!! info "Beta API Only"
    This service is only available when using `APIVersion.BETA`. See [Beta API Overview](index.md) for setup instructions.

## SearchService

::: devrev.services.search.SearchService
    options:
      show_source: true
      members:
        - core
        - hybrid

## AsyncSearchService

::: devrev.services.search.AsyncSearchService
    options:
      show_source: true

## Usage Examples

### Core Search

Core search uses DevRev's query language for precise filtering:

```python
from devrev import DevRevClient, APIVersion
from devrev.models.search import SearchNamespace

client = DevRevClient(api_version=APIVersion.BETA)

# Simple query
results = client.search.core("authentication issues")

for result in results.results:
    print(f"{result.id}: {result.score}")

# Advanced query with filters
results = client.search.core(
    query="type:ticket AND priority:p0 AND status:open",
    namespaces=[SearchNamespace.WORK],
    limit=20,
)
```

### Hybrid Search

Hybrid search combines keyword matching with semantic understanding:

```python
from devrev.models.search import SearchNamespace

# Semantic search for similar concepts
results = client.search.hybrid(
    query="login problems",
    namespaces=[SearchNamespace.CONVERSATION, SearchNamespace.ARTICLE],
    semantic_weight=0.7,  # Favor semantic matching
    limit=10,
)

for result in results.results:
    print(f"{result.id}: {result.score}")
    if result.highlights:
        print(f"  Highlights: {result.highlights}")
```

### Search Across Multiple Namespaces

```python
from devrev.models.search import SearchNamespace

# Search across tickets, conversations, and articles
results = client.search.hybrid(
    query="API authentication",
    namespaces=[
        SearchNamespace.WORK,
        SearchNamespace.CONVERSATION,
        SearchNamespace.ARTICLE,
    ],
    semantic_weight=0.5,
)
```

### Using Request Objects

```python
from devrev.models.search import CoreSearchRequest, HybridSearchRequest, SearchNamespace

# Core search with request object
request = CoreSearchRequest(
    query="type:incident AND severity:sev0",
    namespaces=[SearchNamespace.WORK],
    limit=50,
)
results = client.search.core(request)

# Hybrid search with request object
request = HybridSearchRequest(
    query="database performance issues",
    semantic_weight=0.8,
    limit=20,
)
results = client.search.hybrid(request)
```

### Pagination

```python
# Get first page
results = client.search.core(
    query="status:open",
    limit=50,
)

# Process results
for result in results.results:
    print(result.id)

# Get next page
if results.next_cursor:
    next_results = client.search.core(
        query="status:open",
        cursor=results.next_cursor,
        limit=50,
    )
```

### Async Usage

```python
import asyncio
from devrev import AsyncDevRevClient, APIVersion
from devrev.models.search import SearchNamespace

async def main():
    async with AsyncDevRevClient(api_version=APIVersion.BETA) as client:
        # Core search
        results = await client.search.core(
            query="type:ticket",
            namespaces=[SearchNamespace.WORK],
        )
        
        # Hybrid search
        results = await client.search.hybrid(
            query="authentication issues",
            semantic_weight=0.7,
        )

asyncio.run(main())
```

## Related Models

### SearchNamespace

Enum representing searchable object types:

- `ACCOUNT` - Customer accounts
- `ARTICLE` - Knowledge base articles
- `CONVERSATION` - Customer conversations
- `WORK` - Work items (tickets, issues, tasks)
- `USER` - Users (both dev and rev users)
- `TAG` - Tags
- `PART` - Product parts/components
- `REV_USER` - External customers
- `DEV_USER` - Internal team members

### SearchResponse

Response model containing:

- `results` - List of search results
- `next_cursor` - Pagination cursor for next page
- `total` - Total number of results (if available)

### SearchResult

Individual search result with:

- `id` - Object ID
- `namespace` - Object type
- `score` - Relevance score
- `highlights` - Highlighted matching text
- `summary` - Object summary data

## Query Language (Core Search)

Core search supports advanced query syntax:

### Field Filters
```python
# Filter by field
results = client.search.core("type:ticket")
results = client.search.core("status:open")
results = client.search.core("priority:p0")
```

### Boolean Operators
```python
# AND operator
results = client.search.core("type:ticket AND status:open")

# OR operator
results = client.search.core("priority:p0 OR priority:p1")

# NOT operator
results = client.search.core("type:ticket NOT status:closed")
```

### Phrase Search
```python
# Exact phrase match
results = client.search.core('"database connection error"')
```

### Wildcards
```python
# Wildcard search
results = client.search.core("auth*")  # Matches authentication, authorize, etc.
```

## Best Practices

1. **Choose the right search type**:
   - Use **core search** for precise filtering with known fields
   - Use **hybrid search** for natural language queries and semantic matching

2. **Optimize semantic weight**:
   - `0.0-0.3`: Favor keyword matching (exact terms)
   - `0.4-0.6`: Balanced approach
   - `0.7-1.0`: Favor semantic matching (similar concepts)

3. **Limit namespaces**: Specify namespaces to improve performance and relevance

4. **Use pagination**: Process large result sets in chunks

5. **Leverage highlights**: Use highlighted text to show users why results matched

6. **Cache results**: Cache search results when appropriate to reduce API calls

