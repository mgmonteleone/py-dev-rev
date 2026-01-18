# Changelog

All notable changes to the DevRev Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2026-01-18

🚀 **Beta API Support** - Major release adding support for DevRev Beta API with 74 new endpoints!

This release introduces Beta API support alongside the existing Public API, providing access to advanced features including incident management, customer engagement tracking, AI-powered recommendations, and hybrid search.

### Highlights

- **Beta API Support**: Choose between Public (stable) and Beta (new features) API versions
- **7 New Beta Services**: Incidents, Engagements, Brands, UOMs, Question Answers, Recommendations, Search
- **74 New Endpoints**: Comprehensive coverage of beta API features
- **Fully Backwards Compatible**: All existing Public API functionality unchanged

### Added

#### Beta API Services (#79)
- **IncidentsService** - Incident lifecycle management with SLA integration (6 endpoints)
  - Create, get, list, update, delete, and group incidents
  - Support for incident stages: acknowledged, identified, mitigated, resolved
  - Severity levels: SEV0, SEV1, SEV2, SEV3
- **EngagementsService** - Customer engagement tracking (6 endpoints)
  - Create, get, list, update, delete, and count engagements
  - Support for engagement types: call, email, meeting, default
  - Member and parent relationship tracking
- **BrandsService** - Multi-brand management (5 endpoints)
  - Create, get, list, update, delete brands
  - Brand configuration and customization
- **UomsService** - Unit of Measurement for metering (6 endpoints)
  - Create, get, list, update, delete, count UOMs
  - Aggregation types: sum, minimum, maximum, unique_count, running_total, duration, latest, oldest
  - Metric scopes for usage tracking
- **QuestionAnswersService** - Q&A management (5 endpoints)
  - Create, get, list, update, delete question-answer pairs
  - Knowledge base integration
- **RecommendationsService** - AI-powered recommendations (2 endpoints)
  - Chat completions with OpenAI-compatible interface
  - Reply recommendations for support tickets
- **SearchService** - Advanced search capabilities (2 endpoints)
  - Core search with DevRev query language
  - Hybrid search combining keyword and semantic search
  - Search across multiple namespaces: accounts, articles, conversations, work, users

#### Additional Beta Services (#79)
- **PreferencesService** - User preference management (2 endpoints: get, update)
- **NotificationsService** - Notification sending (1 endpoint: send)
- **TrackEventsService** - Event tracking and analytics (1 endpoint: publish)

#### Configuration & API Version Selection (#79)
- `APIVersion` enum for selecting Public or Beta API
- `DEVREV_API_VERSION` environment variable (default: `public`)
- Client parameter: `DevRevClient(api_version=APIVersion.BETA)`
- Config object support: `DevRevConfig(api_version=APIVersion.BETA)`

#### Exception Handling (#79)
- `BetaAPIRequiredError` - Raised when accessing beta features without beta API enabled
- Clear error messages with migration guidance

#### Models & Enums (#79)
- **Incident Models**: `Incident`, `IncidentStage`, `IncidentSeverity`, `IncidentGroupItem`
- **Engagement Models**: `Engagement`, `EngagementType`
- **Brand Models**: `Brand`, `BrandCreate`, `BrandUpdate`
- **UOM Models**: `Uom`, `UomAggregationType`, `UomMetricScope`
- **Recommendation Models**: `ChatMessage`, `MessageRole`, `ChatCompletionRequest`, `TokenUsage`
- **Search Models**: `SearchNamespace`, `SearchResult`, `CoreSearchRequest`, `HybridSearchRequest`

### Changed

#### Enhanced Services with Beta Endpoints (#79)
- **AccountsService** - Added `count` endpoint (beta only)
- **ArticlesService** - Added `count` endpoint (beta only)
- **ConversationsService** - Added `export` endpoint (beta only)
- **GroupsService** - Added `members.count` endpoint (beta only)

### Configuration

New environment variable:
- `DEVREV_API_VERSION` - API version selection: `public` or `beta` (default: `public`)

### Documentation

- [Beta API Migration Guide](guides/beta-api.md) - Comprehensive migration guide
- [Beta Features Examples](examples/beta-features.md) - Runnable code examples
- [API Differences](api/beta-api-differences.md) - Detailed comparison of Public vs Beta APIs

### Backwards Compatibility

✅ **Fully Backwards Compatible**
- All Public API endpoints continue to work unchanged
- Default API version remains `public` for existing code
- Beta features are opt-in only
- No breaking changes to existing functionality

### Migration Guide

To use beta features:

```python
from devrev import DevRevClient, APIVersion

# Enable beta API
client = DevRevClient(api_version=APIVersion.BETA)

# Access beta services
incidents = client.incidents.list()
search_results = client.search.hybrid("authentication issues")
```

See the [Beta API Migration Guide](guides/beta-api.md) for complete details.

## [1.1.0] - 2026-01-15

### Added
- Connection pooling with configurable limits for improved performance (#78)
- Fine-grained timeout configuration with `TimeoutConfig` class (#78)
- ETag caching for conditional requests to reduce bandwidth (#78)
- Circuit breaker pattern for automatic failure detection and recovery (#78)
- Structured JSON logging with `JSONFormatter` for production environments (#78)
- Health check methods (`health_check()`) for monitoring service availability (#78)
- `CircuitBreakerError` exception for circuit breaker state handling (#78)
- HTTP/2 support (optional, disabled by default) (#78)

### Changed
- Enhanced `DevRevConfig` with new performance and reliability settings (#78)
- Improved HTTP client with connection pooling and keep-alive support (#78)
- Updated logging to support both text and JSON formats (#78)

### Configuration
New environment variables and configuration options:
- `DEVREV_LOG_FORMAT` - Log format: `text` or `json` (default: `text`)
- `DEVREV_MAX_CONNECTIONS` - Maximum connection pool size (default: `100`)
- `DEVREV_MAX_KEEPALIVE_CONNECTIONS` - Maximum keep-alive connections (default: `20`)
- `DEVREV_KEEPALIVE_EXPIRY` - Keep-alive expiry in seconds (default: `30.0`)
- `DEVREV_HTTP2` - Enable HTTP/2 support (default: `false`)
- `DEVREV_CIRCUIT_BREAKER_ENABLED` - Enable circuit breaker (default: `true`)
- `DEVREV_CIRCUIT_BREAKER_THRESHOLD` - Failure threshold (default: `5`)
- `DEVREV_CIRCUIT_BREAKER_RECOVERY_TIMEOUT` - Recovery timeout in seconds (default: `30`)
- `DEVREV_CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS` - Test requests in half-open state (default: `3`)

## [1.0.0] - 2026-01-13

🎉 **First Stable Release** of the DevRev Python SDK!

This release marks the completion of all four development phases, providing a production-ready SDK for interacting with the DevRev API.

### Highlights

- **Complete API Coverage**: Full support for all 209 DevRev public API endpoints
- **Type Safety**: Comprehensive Pydantic v2 models for all requests and responses
- **Sync & Async**: Both synchronous and asynchronous clients for maximum flexibility
- **Production Ready**: Security audited, 80%+ test coverage, and comprehensive documentation

### Added

#### Core SDK (Phase 2)
- `DevRevClient` - Synchronous client with context manager support
- `AsyncDevRevClient` - Async client with async context manager support
- HTTP client layer with automatic retry logic and exponential backoff
- Rate limit handling with Retry-After header support
- Configurable timeouts and max retries

#### Full API Coverage (Phase 3)
- **14 Service Classes** with both sync and async implementations:
  - `AccountsService` - Customer account management (7 endpoints)
  - `WorksService` - Work items: tickets, issues, tasks (6 endpoints)
  - `DevUsersService` - Internal user management (10 endpoints)
  - `RevUsersService` - External user management (7 endpoints)
  - `PartsService` - Product parts and components (5 endpoints)
  - `ArticlesService` - Knowledge base articles (5 endpoints)
  - `ConversationsService` - Customer conversations (5 endpoints)
  - `TagsService` - Tagging and categorization (5 endpoints)
  - `GroupsService` - User group management (6 endpoints)
  - `WebhooksService` - Webhook configuration (6 endpoints)
  - `SlasService` - Service level agreements (6 endpoints)
  - `TimelineEntriesService` - Activity timeline (5 endpoints)
  - `LinksService` - Object relationships (5 endpoints)
  - `CodeChangesService` - Code change tracking (5 endpoints)

#### Pydantic Models
- 130+ Pydantic v2 models with strict validation
- Enums for type-safe status, priority, and severity values
- Date filters and pagination models
- Request/response models for all endpoints

#### Pagination Utilities
- `Paginator` and `AsyncPaginator` classes for iterating through results
- Cursor-based pagination following DevRev API patterns
- Helper functions: `paginate()` and `async_paginate()`

#### Documentation (Phase 4)
- Documentation site with MkDocs Material theme
- Comprehensive API reference documentation
- Tutorials and guides for common use cases
- Example applications (basic, advanced, integrations)
- Getting started guide with authentication options

#### Examples
- Basic examples: list accounts, create work items, search users
- Async example with concurrent requests
- Pagination and error handling examples
- Integration examples: FastAPI, Flask, Google Cloud Functions

#### Testing & Quality
- 180+ unit tests with 80%+ code coverage
- Integration test scaffolding for API validation
- Performance benchmarking framework
- ruff linting and mypy strict type checking

#### Security
- **HTTPS Enforcement**: Validation rejects insecure HTTP URLs in `base_url`
- Security audit completed with `bandit` (5,189 lines scanned, 0 issues)
- Dependency audit completed with `pip-audit` (0 known vulnerabilities)
- Token masking with Pydantic `SecretStr`
- SECURITY.md with security policy and best practices

#### CI/CD
- GitHub Actions workflows for CI, documentation, and release
- Automated release workflow triggered by version tags
- Dependabot configuration for dependency updates

### Developer Experience

- Full type annotations with mypy strict mode compliance
- IDE autocomplete support with comprehensive type hints
- Google-style docstrings throughout
- Colored logging support with configurable levels
- Environment-based configuration

### Python Support

- Python 3.11, 3.12, and 3.13 supported
- N-2 version support policy

## [0.1.0] - 2026-01-12

### Added
- Initial release of DevRev Python SDK
- Full API coverage for 209 DevRev public endpoints
- Synchronous and asynchronous clients (`DevRevClient`, `AsyncDevRevClient`)
- Pydantic v2 models for all requests and responses
- Automatic retry with exponential backoff
- Rate limit handling with Retry-After support
- Comprehensive exception hierarchy
- Environment-based configuration
- Colored logging support

### Services Implemented
- Accounts (7 endpoints)
- Works (6 endpoints)
- Dev Users (10 endpoints)
- Rev Users (7 endpoints)
- Parts (5 endpoints)
- Articles (5 endpoints)
- Conversations (5 endpoints)
- Tags (5 endpoints)
- Groups (6 endpoints)
- Webhooks (6 endpoints)
- SLAs (6 endpoints)
- Timeline Entries (5 endpoints)
- Links (5 endpoints)
- Code Changes (5 endpoints)

### Developer Experience
- Full type annotations
- IDE autocomplete support
- Comprehensive docstrings
- Unit and integration test suite (80%+ coverage)

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 2.0.0 | 2026-01-18 | 🚀 Beta API support with 74 new endpoints |
| 1.1.0 | 2026-01-15 | Performance & reliability enhancements |
| 1.0.0 | 2026-01-13 | 🎉 First stable release - Production ready |
| 0.1.0 | 2026-01-12 | Initial development release |

## Upgrading

### From 1.x to 2.0.0

The v2.0.0 release is **fully backwards compatible** with v1.x:

- **No Breaking Changes**: All existing Public API code continues to work
- **Beta API is Opt-In**: Default API version remains `public`
- **New Features**: 7 new beta services with 74 endpoints available when you enable beta API
- **New Exception**: `BetaAPIRequiredError` raised when accessing beta features without beta API enabled

To use beta features, simply enable the beta API:

```python
from devrev import DevRevClient, APIVersion

# Enable beta API
client = DevRevClient(api_version=APIVersion.BETA)
```

See the [Beta API Migration Guide](guides/beta-api.md) for complete details.

### From 0.1.0 to 1.0.0

The v1.0.0 release includes one breaking change and several enhancements:

- **HTTPS Required (Breaking Change)**: The SDK now enforces HTTPS URLs for `base_url`. If you were using HTTP URLs (e.g., for local testing), you will need to update to HTTPS. Note that the official DevRev API only supports HTTPS, so this should not affect production usage.
- **New Services**: 10 additional service classes are now available
- **Enhanced Error Messages**: More detailed error information is provided

All existing API calls remain compatible - only the HTTPS enforcement may require configuration changes for non-production environments.

## Reporting Issues

Found a bug or have a suggestion? Please [open an issue](https://github.com/mgmonteleone/py-dev-rev/issues/new).

