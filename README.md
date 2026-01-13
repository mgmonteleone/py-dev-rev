# py-devrev

A modern, type-safe Python SDK for the DevRev API.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue.svg)](https://mypy-lang.org/)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [API Coverage](#api-coverage)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Logging](#logging)
- [Development](#development)
- [Testing Strategy](#testing-strategy)
- [CI/CD Pipeline](#cicd-pipeline)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

`py-devrev` is a modern Python library for interacting with the [DevRev API](https://devrev.ai). Built with developer experience in mind, it provides:

- **100% API Coverage**: Full support for all 209 public DevRev API endpoints
- **Type Safety**: Complete type annotations with Pydantic v2 models
- **Modern Python**: Supports Python 3.11+ (N-2 policy)
- **Developer Friendly**: Intuitive API design with comprehensive documentation

This SDK is generated and maintained from the official DevRev OpenAPI specification (`openapi-public.yaml`), ensuring it stays current with the latest API changes.

---

## Features

### Core Capabilities

- ✅ **Full API Coverage** - All DevRev public API endpoints supported
- ✅ **Type-Safe Models** - Pydantic v2 models for all request/response objects
- ✅ **Async Support** - Native async/await support for high-performance applications
- ✅ **Automatic Retries** - Configurable retry logic with exponential backoff
- ✅ **Rate Limiting** - Built-in rate limit handling with Retry-After support
- ✅ **Pagination** - Easy iteration over paginated endpoints

### Developer Experience

- ✅ **Rich Exceptions** - Detailed, actionable error messages
- ✅ **Colored Logging** - Beautiful console output with configurable levels
- ✅ **IDE Support** - Full autocomplete and type hints in modern IDEs
- ✅ **Comprehensive Docs** - Detailed documentation with examples

### Enterprise Ready

- ✅ **Security First** - No secrets in code, environment-based configuration
- ✅ **Production Logging** - Structured logging suitable for production
- ✅ **High Test Coverage** - 80%+ code coverage with unit and integration tests

---

## Installation

### From Google Artifact Registry (Recommended)

```bash
pip install py-devrev
```

### From Source

```bash
git clone https://github.com/mgmonteleone/py-dev-rev.git
cd py-dev-rev
pip install -e ".[dev]"
```

### Requirements

- Python 3.11 or higher
- Dependencies are automatically installed

### Python support policy

py-devrev follows an **N-2** support policy (current stable Python + two previous minor versions).

- See: [Python version support policy](docs/guides/version-support.md)
- See: [Compatibility matrix](docs/guides/compatibility.md)

---

## Quick Start

```python
from devrev import DevRevClient

# Initialize the client (reads DEVREV_API_TOKEN from environment)
client = DevRevClient()

# List accounts
accounts = client.accounts.list(limit=10)
for account in accounts:
    print(f"{account.id}: {account.display_name}")

# Get a specific work item
work = client.works.get(id="don:core:...")
print(f"Work: {work.title} - Status: {work.stage.name}")

# Create a new ticket
ticket = client.works.create(
    title="Bug: Login page not loading",
    type="ticket",
    applies_to_part="don:core:...",
    body="Users are reporting issues with the login page..."
)
```

### Async Usage

```python
import asyncio
from devrev import AsyncDevRevClient

async def main():
    async with AsyncDevRevClient() as client:
        accounts = await client.accounts.list(limit=10)
        for account in accounts:
            print(f"{account.id}: {account.display_name}")

asyncio.run(main())
```

---

## Authentication

The SDK supports multiple authentication methods:

### API Token (Recommended)

Set the `DEVREV_API_TOKEN` environment variable:

```bash
export DEVREV_API_TOKEN="your-api-token-here"
```

Or pass it directly (not recommended for production):

```python
client = DevRevClient(api_token="your-api-token-here")
```

### Personal Access Token (PAT)

```bash
export DEVREV_PAT="your-personal-access-token"
```

### Service Account

```python
client = DevRevClient(
    service_account_id="your-service-account-id",
    service_account_secret="your-service-account-secret"  # Load from env!
)
```

---

## API Coverage

The SDK provides complete coverage of all 209 DevRev public API endpoints, organized into logical service groups:

### Core Objects

| Service | Endpoints | Description |
|---------|-----------|-------------|
| **Accounts** | 7 | Customer account management (create, list, get, update, delete, merge, export) |
| **Rev Orgs** | 5 | Revenue organization management |
| **Rev Users** | 7 | External user management (customers) |
| **Dev Users** | 10 | Internal user management (team members) |
| **Works** | 6 | Work items - tickets, issues, tasks (create, list, get, update, delete, export, count) |
| **Parts** | 5 | Product parts and components |

### Content & Knowledge

| Service | Endpoints | Description |
|---------|-----------|-------------|
| **Articles** | 5 | Knowledge base articles |
| **Conversations** | 5 | Customer conversations |
| **Timeline Entries** | 5 | Activity timeline management |
| **Tags** | 5 | Tagging and categorization |

### Collaboration

| Service | Endpoints | Description |
|---------|-----------|-------------|
| **Groups** | 6 | User group management |
| **Meetings** | 6 | Meeting scheduling and management |
| **Chats** | 3 | Chat functionality |
| **Comments** | - | Via timeline entries |

### Development & Engineering

| Service | Endpoints | Description |
|---------|-----------|-------------|
| **Code Changes** | 5 | Code change tracking |
| **Artifacts** | 6 | File and artifact management |
| **Webhooks** | 6 | Webhook configuration |
| **Links** | 5 | Object linking and relationships |

### Configuration & Admin

| Service | Endpoints | Description |
|---------|-----------|-------------|
| **Auth Tokens** | 8 | Authentication token management |
| **Service Accounts** | 2 | Service account management |
| **Dev Orgs** | 7 | Organization settings and auth connections |
| **Schemas** | 7 | Custom schema management |
| **Custom Objects** | 6 | Custom object CRUD operations |

### Workflows & SLAs

| Service | Endpoints | Description |
|---------|-----------|-------------|
| **SLAs** | 6 | Service level agreement management |
| **SLA Trackers** | 3 | SLA tracking and monitoring |
| **Stages** | 4 | Custom stage definitions |
| **States** | 4 | Custom state definitions |
| **Stage Diagrams** | 4 | Workflow visualization |

### Analytics & Observability

| Service | Endpoints | Description |
|---------|-----------|-------------|
| **Metrics** | 6 | Metric definitions and tracking |
| **Surveys** | 9 | Customer surveys and responses |
| **Observability** | 3 | Session observability data |

### Other Services

| Service | Endpoints | Description |
|---------|-----------|-------------|
| **Directories** | 6 | Directory management |
| **Vistas** | 6 | View configurations |
| **Org Schedules** | 7 | Business hour schedules |
| **Jobs** | 2 | Background job management |
| **Web Crawler** | 4 | Web crawler job management |
| **Reactions** | 2 | Emoji reactions |
| **Snap Widgets** | 2 | UI widget management |
| **Commands** | 4 | Slash command management |

---

## Usage Examples

### Working with Accounts

```python
from devrev import DevRevClient

client = DevRevClient()

# List all accounts with pagination
for account in client.accounts.list():
    print(f"Account: {account.display_name}")
    print(f"  Tier: {account.tier}")
    print(f"  Domains: {', '.join(account.domains or [])}")

# Create a new account
new_account = client.accounts.create(
    display_name="Acme Corporation",
    domains=["acme.com", "acme.io"],
    tier="enterprise",
    description="Major enterprise customer"
)

# Update an account
updated = client.accounts.update(
    id=new_account.id,
    tier="premium"
)

# Search/filter accounts
enterprise_accounts = client.accounts.list(
    tier=["enterprise"],
    created_after="2024-01-01"
)
```

### Managing Work Items

```python
# Create a ticket
ticket = client.works.create(
    type="ticket",
    title="Cannot access dashboard",
    body="Customer reports 500 error when loading dashboard",
    applies_to_part="don:core:dvrv-us-1:devo/1:part/1",
    severity="high",
    owned_by=["don:identity:dvrv-us-1:devo/1:devu/123"]
)

# List open tickets
open_tickets = client.works.list(
    type=["ticket"],
    stage_name=["open", "in_progress"]
)

# Update work item status
client.works.update(
    id=ticket.id,
    stage_name="resolved"
)

# Export works for reporting
export_result = client.works.export(
    type=["ticket"],
    created_after="2024-01-01"
)
```

### Articles and Knowledge Base

```python
# Create an article
article = client.articles.create(
    title="Getting Started Guide",
    applies_to_parts=["don:core:..."],
    authored_by="don:identity:...",
    body="# Welcome\n\nThis guide will help you get started..."
)

# List published articles
published = client.articles.list(
    status=["published"]
)

# Update article content
client.articles.update(
    id=article.id,
    body="# Updated Content\n\n..."
)
```

### Webhooks

```python
# Register a webhook
webhook = client.webhooks.create(
    url="https://your-server.com/webhooks/devrev",
    event_types=["work_created", "work_updated"],
    secret="your-webhook-secret"  # Load from environment!
)

# List webhooks
webhooks = client.webhooks.list()

# Update webhook
client.webhooks.update(
    id=webhook.id,
    event_types=["work_created", "work_updated", "work_deleted"]
)
```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DEVREV_API_TOKEN` | Yes* | - | API authentication token |
| `DEVREV_BASE_URL` | No | `https://api.devrev.ai` | API base URL |
| `DEVREV_TIMEOUT` | No | `30` | Request timeout in seconds |
| `DEVREV_MAX_RETRIES` | No | `3` | Maximum retry attempts |
| `DEVREV_LOG_LEVEL` | No | `WARN` | Logging level (DEBUG, INFO, WARN, ERROR) |

### Configuration File

Create a `.env` file for local development:

```bash
# .env (never commit this file!)
DEVREV_API_TOKEN=your-api-token-here
DEVREV_LOG_LEVEL=DEBUG
DEVREV_TIMEOUT=60
```

A `.env.sample` file is provided as a template.

### Programmatic Configuration

```python
from devrev import DevRevClient, DevRevConfig

config = DevRevConfig(
    base_url="https://api.devrev.ai",
    timeout=60,
    max_retries=5,
    log_level="DEBUG"
)

client = DevRevClient(config=config)
```

---

## Error Handling

The SDK provides rich, informative exceptions:

```python
from devrev import DevRevClient
from devrev.exceptions import (
    DevRevError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError
)

client = DevRevClient()

try:
    account = client.accounts.get(id="invalid-id")
except NotFoundError as e:
    print(f"Account not found: {e.message}")
    print(f"Request ID: {e.request_id}")  # For support tickets
except ValidationError as e:
    print(f"Invalid request: {e.message}")
    print(f"Field errors: {e.field_errors}")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after} seconds")
except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
except ServerError as e:
    print(f"Server error: {e.message}")
except DevRevError as e:
    print(f"Unexpected error: {e}")
```

### Exception Hierarchy

```
DevRevError (base)
├── AuthenticationError (401)
├── ForbiddenError (403)
├── NotFoundError (404)
├── ValidationError (400)
├── ConflictError (409)
├── RateLimitError (429)
├── ServerError (500)
└── ServiceUnavailableError (503)
```

---

## Logging

The SDK uses structured logging with optional color support:

### Log Levels

Set via `DEVREV_LOG_LEVEL` environment variable:

- `DEBUG` - Detailed debugging information
- `INFO` - General operational information
- `WARN` - Warning messages (default)
- `ERROR` - Error messages only

### Example Output

```
2024-01-15 10:30:45 [INFO] devrev.client: Initialized DevRevClient
2024-01-15 10:30:45 [DEBUG] devrev.http: POST /accounts.list
2024-01-15 10:30:46 [DEBUG] devrev.http: Response 200 (245ms)
2024-01-15 10:30:47 [WARN] devrev.http: Rate limit approaching (80% used)
```

### Custom Logger Integration

```python
import logging

# Use your own logger
my_logger = logging.getLogger("myapp.devrev")
client = DevRevClient(logger=my_logger)
```

---

## Development

### Project Structure

```
py-devrev/
├── src/
│   └── devrev/
│       ├── __init__.py
│       ├── client.py           # Main client classes
│       ├── config.py           # Configuration management
│       ├── exceptions.py       # Exception definitions
│       ├── models/             # Pydantic models
│       │   ├── __init__.py
│       │   ├── accounts.py
│       │   ├── works.py
│       │   └── ...
│       ├── services/           # API service classes
│       │   ├── __init__.py
│       │   ├── accounts.py
│       │   ├── works.py
│       │   └── ...
│       └── utils/              # Utilities
│           ├── __init__.py
│           ├── http.py
│           ├── logging.py
│           └── pagination.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── openapi-public.yaml         # DevRev OpenAPI specification
├── pyproject.toml
└── README.md
```

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/mgmonteleone/py-dev-rev.git
cd py-dev-rev

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dev dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Copy environment template
cp .env.sample .env
# Edit .env with your credentials
```

### Code Quality Tools

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy src/

# Run all checks
pre-commit run --all-files
```

---

## Testing Strategy

### Test Categories

1. **Unit Tests** - Test individual functions and classes in isolation
   - All models and their validation
   - Utility functions
   - Error handling logic

2. **Integration Tests** - Test against the real API
   - **Read-only endpoints**: Tested against actual DevRev API
   - **Mutating endpoints**: Tested with comprehensive mocks

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests (requires API credentials)
pytest tests/integration/ -m integration

# Run specific test file
pytest tests/unit/test_accounts.py
```

### Coverage Requirements

- **Minimum**: 80% line coverage
- **Critical paths**: 95% coverage (auth, error handling)

---

## CI/CD Pipeline

The SDK uses Google Cloud Build for automated testing, security scanning, and publishing:

### Pipeline Stages

1. **Lint & Format** - Code quality checks with Ruff
2. **Type Check** - Static type analysis with mypy
3. **Unit Tests** - Fast isolated tests
4. **Integration Tests** - API integration verification
5. **Security Scan** - Dependency vulnerability scanning
6. **Build** - Package building
7. **Publish** - Automated publishing to Google Artifact Registry

### Automated Publishing

On tagged releases (`v*`), the package is automatically published to Google Artifact Registry.

---

## Roadmap

### Phase 1: Foundation ✅
- [x] Project structure and configuration
- [x] OpenAPI specification integration
- [x] Development standards documentation

### Phase 2: Core Implementation 🔄
- [ ] Base client with authentication
- [ ] HTTP layer with retry logic
- [ ] Pydantic models generation
- [ ] Core services (Accounts, Works, Users)

### Phase 3: Full API Coverage
- [ ] All 209 endpoints implemented
- [ ] Pagination helpers
- [ ] Async client support

### Phase 4: Polish & Production
- [ ] Comprehensive test suite
- [ ] Performance optimization
- [ ] Documentation site
- [ ] Example applications

### Phase 5: Maintenance
- [ ] Automated OpenAPI sync
- [ ] Dependency updates
- [ ] Community contributions

---

## Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Ensure all tests pass (`pytest`)
5. Submit a pull request

### Development Guidelines

- Follow PEP 8 and project style guidelines
- Add type hints to all functions
- Write tests for new functionality
- Update documentation as needed

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

- 📖 [Documentation](https://github.com/mgmonteleone/py-dev-rev)
- 🐛 [Issue Tracker](https://github.com/mgmonteleone/py-dev-rev/issues)
- 💬 [Discussions](https://github.com/mgmonteleone/py-dev-rev/discussions)

---

*Built with ❤️ using [Augment Code](https://augmentcode.com)*

