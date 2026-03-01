# Articles Service

Manage knowledge base articles in DevRev.

## ArticlesService

::: devrev.services.articles.ArticlesService
    options:
      show_source: true

## AsyncArticlesService

::: devrev.services.articles.AsyncArticlesService
    options:
      show_source: true

## Usage Examples

### List Articles

```python
from devrev import DevRevClient
from devrev.models.articles import ArticlesListRequest

client = DevRevClient()

# Using a request object
request = ArticlesListRequest(limit=20)
articles = client.articles.list(request)
for article in articles:
    print(f"{article.title}")
```

### Get Article

```python
from devrev.models.articles import ArticlesGetRequest

request = ArticlesGetRequest(id="don:core:dvrv-us-1:devo/1:article/123")
article = client.articles.get(request)
print(f"Article: {article.title}")
if article.description:
    print(f"Description: {article.description[:100]}...")
```

### Create Article (Simple - Metadata Only)

```python
from devrev.models.articles import ArticlesCreateRequest

request = ArticlesCreateRequest(
    title="Getting Started Guide",
    description="# Welcome\n\nThis guide helps you get started...",
    owned_by=["don:identity:dvrv-us-1:devo/1:devu/1"],  # Required: list of dev user IDs
)
article = client.articles.create(request)
print(f"Created: {article.id}")
```

### Create Article with Content (Recommended)

The unified `create_with_content()` method automatically handles artifact storage:

```python
from devrev.models.articles import ArticleStatus

# Simple 3-line creation with content
article = client.articles.create_with_content(
    title="Getting Started Guide",
    content="<h1>Welcome</h1><p>This guide helps you get started...</p>",
    owned_by=["don:identity:dvrv-us-1:devo/1:devu/1"],
    description="Short summary for search/listing",  # Optional metadata
    status=ArticleStatus.PUBLISHED,  # Optional: draft, published, archived
    content_format="text/html",  # Optional: default is text/html
)
print(f"Created article with content: {article.id}")
```

**Before** (15+ lines with manual artifact handling):
```python
# Old way - complex multi-step workflow
from devrev.models.artifacts import ArtifactPrepareRequest

# Step 1: Prepare artifact
prepare_req = ArtifactPrepareRequest(
    file_name="getting-started.html",
    file_type="text/html",
    configuration_set="article_media",
)
prepare_resp = client.artifacts.prepare(prepare_req)

# Step 2: Upload content
client.artifacts.upload(prepare_resp, "<h1>Welcome</h1>...")

# Step 3: Create article with reference
article_req = ArticlesCreateRequest(
    title="Getting Started Guide",
    owned_by=["don:identity:dvrv-us-1:devo/1:devu/1"],
    resource={"content_artifact": prepare_resp.id},
)
article = client.articles.create(article_req)
```

**After** (3 lines with unified method):
```python
# New way - simple one-step operation
article = client.articles.create_with_content(
    title="Getting Started Guide",
    content="<h1>Welcome</h1><p>This guide helps you get started...</p>",
    owned_by=["don:identity:dvrv-us-1:devo/1:devu/1"],
)
```

### Get Article with Content

```python
# Get metadata only (fast, no content download)
article = client.articles.get_with_content("don:core:dvrv-us-1:devo/1:article/123")

# Access both metadata and content
print(f"Title: {article.article.title}")
print(f"Status: {article.article.status}")
print(f"Content: {article.content[:100]}...")
print(f"Format: {article.content_format}")
```

### Update Article Content

```python
# Update only the content (metadata unchanged)
updated_article = client.articles.update_content(
    id="don:core:dvrv-us-1:devo/1:article/123",
    content="<h1>Updated Content</h1><p>New version of the article...</p>",
    content_format="text/html",  # Optional
)
print(f"Content updated: {updated_article.id}")
```

### Update Article with Content

```python
# Update both metadata and content in one call
updated_article = client.articles.update_with_content(
    id="don:core:dvrv-us-1:devo/1:article/123",
    title="Updated Getting Started Guide",  # Optional
    content="<h1>Updated Welcome</h1>...",  # Optional
    description="Updated summary",  # Optional
    status=ArticleStatus.PUBLISHED,  # Optional
)

# Or update only metadata
updated_article = client.articles.update_with_content(
    id="don:core:dvrv-us-1:devo/1:article/123",
    title="New Title",
    status=ArticleStatus.ARCHIVED,
)

# Or update only content
updated_article = client.articles.update_with_content(
    id="don:core:dvrv-us-1:devo/1:article/123",
    content="<h1>New Content</h1>",
)
```

### Async Usage

All unified methods are available in async versions:

```python
from devrev import AsyncDevRevClient
from devrev.models.articles import ArticleStatus

async def create_article():
    client = AsyncDevRevClient()

    # Create with content
    article = await client.articles.create_with_content(
        title="Async Article",
        content="<h1>Created asynchronously</h1>",
        owned_by=["don:identity:dvrv-us-1:devo/1:devu/1"],
    )

    # Get with content
    article_with_content = await client.articles.get_with_content(article.id)

    # Update content
    updated = await client.articles.update_content(
        id=article.id,
        content="<h1>Updated Content</h1>",
    )

    return updated
```

## Method Comparison

| Method | Use Case | Lines of Code | Artifact Handling |
|--------|----------|---------------|-------------------|
| `create()` | Metadata only | 5-7 | Manual (separate steps) |
| `create_with_content()` | Create with content | 3-5 | Automatic |
| `get()` | Metadata only | 2-3 | N/A |
| `get_with_content()` | Get with content | 1-2 | Automatic |
| `update()` | Metadata only | 3-5 | N/A |
| `update_content()` | Content only | 2-4 | Automatic |
| `update_with_content()` | Metadata and/or content | 2-6 | Automatic |

**Recommendation**: Use the `*_with_content()` methods for all article operations that involve body content. They provide a simpler API and handle artifact management automatically.

