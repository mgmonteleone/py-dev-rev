# Changelog

All notable changes to the DevRev Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **MCP Server: Per-user DevRev PAT authentication** (#145) — The MCP server now supports per-user authentication using DevRev Personal Access Tokens. Each user sends their own DevRev PAT as the Bearer token, which the server validates against the DevRev API and uses to create a per-request client. This provides better security, audit trails, and eliminates shared secrets.
  - New auth mode: `MCP_AUTH_MODE=devrev-pat` (default)
  - Domain restrictions: `MCP_AUTH_ALLOWED_DOMAINS` to limit access by email domain
  - Token caching: `MCP_AUTH_CACHE_TTL_SECONDS` for validation cache (default 5 minutes)
  - Legacy mode: `MCP_AUTH_MODE=static-token` still supported for backward compatibility
  - Updated Cloud Run deployment to use per-user PAT mode by default
  - Updated documentation and client configuration examples

### Fixed
- **SDK: Articles API field naming** — Fixed field name from `content` to `description` to match DevRev API specification. Updated `Article`, `ArticlesCreateRequest`, and `ArticlesUpdateRequest` models. **BREAKING CHANGE**: Code using `article.content` or `ArticlesCreateRequest(content=...)` must be updated to use `description` instead.

### Changed
- **SDK: Migrated all enums from `(str, Enum)` to `StrEnum`** — 32 enum classes across 21 files now use Python 3.11+ `StrEnum` instead of the legacy `(str, Enum)` pattern. This resolves ruff UP042 linting errors and aligns with modern Python best practices. Note: `str(EnumMember)` now returns the value string directly (e.g., `"active"`) instead of `"ClassName.MEMBER"`. (#138)

## [2.3.1] - 2026-02-24

### Fixed

- **DevUserState enum missing states** (#126) - Added missing `DELETED`, `LOCKED`, and `UNASSIGNED` states to the `DevUserState` enum to match the DevRev API `user-state` schema. This is the same fix previously applied to `RevUserState` in v2.1.1 (#115). This fixes Pydantic validation errors when the API returns dev users with these states.

## [2.3.0] - 2026-02-11

### Added
- **Client-side re-ranking** for hybrid search — boosts results where query is a substring of display_name/title
- **Dynamic `_extract_display_name`** — supports all 35 DevRev namespace types for re-ranking
- **MCP Inspector compatibility** — `__main__.py` uses `parse_known_args()` to handle extra arguments

### Fixed
- **SDK: SearchNamespace enum** — Expanded from 9 to 35 values matching all API-supported namespaces
- **SDK: Namespace serialization** — Fixed `namespaces` (plural) → `namespace` (singular) via `serialization_alias`
- **SDK: Namespace type** — Fixed from `list[SearchNamespace]` to single `SearchNamespace` value
- **SDK: SearchResult model** — Restructured with entity-specific dicts, added `modified_date` and `comments` fields
- **SDK: Limit validation** — Added `Field(ge=0, le=50)` to enforce API constraints (was default 25/max 100, now 10/50)
- **Core search ordering** — `devrev_search_core` no longer applies re-ranking, preserving API ordering
- **Namespace parsing resilience** — Handles whitespace, embedded quotes, and case variations from MCP Inspector

### Changed
- Search limit defaults changed from 25 → 10 (matches DevRev API default)
- Search limit maximum changed from 100 → 50 (matches DevRev API constraint)

## [2.2.0] - 2026-02-09

### Added - DevRev MCP Server (Model Context Protocol)

This release introduces a full-featured MCP server that exposes the entire DevRev platform as AI-accessible tools, resources, and prompts.

#### Phase 1: Core Foundation
- FastMCP server with async DevRev client lifecycle management
- `MCPServerConfig` (pydantic-settings) with 14+ configurable environment variables
- 22 initial tools: Works (7), Accounts (6), Users (5), Search beta (2), Recommendations beta (2)
- Pagination utilities with configurable page sizes
- Error formatting and model serialization helpers
- **SDK bug fix**: Enum conversion — `WorkType("TICKET")` fails because `str` enums have lowercase values; fixed to use `WorkType["TICKET"]` (bracket access by name)

#### Phase 2: Full Tool Coverage
- 42 additional tools across 7 modules: Conversations (6), Articles (6), Parts (5), Tags (5), Groups (8), Incidents beta (6), Engagements beta (6)
- Comprehensive KeyError handling for all enum conversions (ArticleStatus, EngagementType, PartType, GroupType, IncidentStage, IncidentSeverity)
- ValueError handling for datetime parsing in engagements

#### Phase 3: Resources & Prompts
- 7 resource templates with `devrev://` URI scheme (ticket, account, article, user/dev, user/rev, part, conversation)
- 8 workflow prompts: triage_ticket, draft_customer_response, escalate_ticket, summarize_account, investigate_issue, weekly_support_report, find_similar_tickets, onboard_customer
- Timeline tools (5), Links tools (4), SLA tools (5)

#### Phase 4: Transport & Security
- Multi-transport support: stdio (default), streamable-http (production), SSE (legacy)
- CLI arguments: `--transport`, `--host`, `--port`
- Bearer token authentication with timing-attack protection (`secrets.compare_digest`)
- Token-bucket rate limiting with LRU eviction (bounded memory, thread-safe)
- Health check endpoint (`GET /health`) with uptime tracking
- Destructive tool gating via `MCP_ENABLE_DESTRUCTIVE_TOOLS`
- DNS rebinding protection and CORS configuration

#### Phase 5: Polish & Deployment
- Dockerfile with multi-stage build and non-root user
- Docker Compose for local development
- Cloud Build configuration for Google Cloud Run deployment
- Comprehensive documentation in README.md
- This changelog entry

#### Bug Fixes (E2E Testing)
- **Critical: HTTP middleware never registered** — `FastMCP` creates its internal Starlette app lazily inside `streamable_http_app()` and `sse_app()`, not at construction time. The health endpoint, bearer token auth middleware, and rate limiting middleware were silently never injected. Fixed by monkey-patching `streamable_http_app()` and `sse_app()` on the `mcp` instance to inject middleware after the Starlette app is created.
- Confirmed 12/14 real API E2E tests pass (2 environmental: SLA 403 permissions, Search 400 beta not enabled)

### Fixed
- All enum conversions across tool modules now use bracket access (by name) with KeyError guards
- `datetime.fromisoformat()` calls wrapped in ValueError handlers
- Rate limiter: zero-RPM config no longer causes ZeroDivisionError
- Auth middleware: timing-safe token comparison prevents side-channel attacks
- Health endpoint: uptime calculated from lifespan init, not module import

## [2.1.2] - 2026-01-28

### Fixed

- **Work.applies_to_part fails to parse API response** (#120) - The DevRev API returns `applies_to_part` as a rich `PartSummary` object in responses, not just a string ID. This caused `pydantic.ValidationError` when parsing API responses. Fixed by:
  - Expanding `PartSummary` model to include `type`, `display_id`, `state`, and `owned_by` fields
  - Changing `Work.applies_to_part` type from `str | None` to `PartSummary | str | None`
  - This is fully backward compatible - string IDs are still accepted for requests

## [2.1.1] - 2026-01-23

### Fixed

- **RevUserState enum missing states** (#115) - Added missing `DEACTIVATED`, `LOCKED`, `SHADOW`, and `UNASSIGNED` states to the `RevUserState` enum to match the DevRev API `user-state` schema. This fixes Pydantic validation errors when the API returns users with these states.

## [2.0.0] - 2026-01-18

🚀 **Major Release** - Beta API support, performance enhancements, and 100% integration test coverage!

### Breaking Changes

#### GroupsMembersCountRequest Parameter Rename (#107)

**Breaking Change**: The `members_count` method parameter and `GroupsMembersCountRequest` model field were renamed to match the actual DevRev API field names.

**Changes Made**:
- **Method Parameter**: `members_count(id=...)` → `members_count(group_id=...)`
- **Model Field**: `GroupsMembersCountRequest.id` → `GroupsMembersCountRequest.group`

**Reason**: The OpenAPI specification and actual API use `group` as the field name, not `id`. This change aligns the SDK with the real API behavior discovered during integration testing.

**Migration**:
```python
# Before (incorrect)
count = client.groups.members_count(id="don:identity:dvrv-us-1:devo/abc123:group/xyz789")

# After (correct)
count = client.groups.members_count(group_id="don:identity:dvrv-us-1:devo/abc123:group/xyz789")
```

**Note**: There are no known existing consumers of this SDK, so the impact is minimal.

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

### Performance & Reliability (#78)

- Connection pooling with configurable limits for improved performance
- Fine-grained timeout configuration with `TimeoutConfig` class
- ETag caching for conditional requests to reduce bandwidth
- Circuit breaker pattern for automatic failure detection and recovery
- Structured JSON logging with `JSONFormatter` for production environments
- Health check methods (`health_check()`) for monitoring service availability
- `CircuitBreakerError` exception for circuit breaker state handling
- HTTP/2 support (optional, disabled by default)

### Integration Testing (#103, #104, #105, #106)

- 100% integration test coverage for all read-only endpoints
- Write operation testing strategy with TestDataManager
- Comprehensive integration test suite with 81 tests

### Bug Fixes

- Fix httpx URL resolution issues with leading slashes (#78)
- Fix circuit breaker off-by-one bug in HALF_OPEN transition (#78)
- Fix request attribute on synthetic 304 response (#78)
- Remove unused exception variables for linting (#76, #77)
- Address security audit findings (#76, #77)

### Changed
- Enhanced `DevRevConfig` with new performance and reliability settings
- Improved HTTP client with connection pooling and keep-alive support
- Updated logging to support both text and JSON formats

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
- `DEVREV_API_VERSION` - API version selection: `public` or `beta` (default: `public`)

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
| 2.3.1 | 2026-02-24 | 🐛 Fix DevUserState enum missing states |
| 2.3.0 | 2026-02-11 | 🔍 Search SDK improvements & client-side re-ranking |
| 2.2.0 | 2026-02-09 | 🤖 MCP Server - Full DevRev platform as AI-accessible tools |
| 2.1.2 | 2026-01-28 | 🐛 Fix Work.applies_to_part parsing for API responses |
| 2.1.1 | 2026-01-23 | 🐛 Fix RevUserState enum missing states |
| 2.0.0 | 2026-01-18 | 🚀 Beta API support, performance enhancements, breaking change |
| 1.0.0 | 2026-01-13 | 🎉 First stable release - Production ready |
| 0.1.0 | 2026-01-12 | Initial development release |

## Upgrading

### From 1.0.0 to 2.0.0

The v2.0.0 release includes Beta API support, performance enhancements, and one breaking change:

#### Breaking Change

- **GroupsMembersCountRequest Parameter Rename**: `members_count(id=...)` → `members_count(group_id=...)`

#### New Features

- **Beta API Support**: 7 new beta services with 74 endpoints available when you enable beta API
- **Performance Enhancements**: Connection pooling, circuit breaker, ETag caching
- **Integration Tests**: 100% coverage of read-only endpoints

To use beta features, enable the beta API:

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

