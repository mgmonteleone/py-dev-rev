# Changelog

All notable changes to the DevRev Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

No unreleased changes yet.

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
| 1.0.0 | 2026-01-13 | 🎉 First stable release - Production ready |
| 0.1.0 | 2026-01-12 | Initial development release |

## Upgrading

### From 0.1.0 to 1.0.0

The v1.0.0 release includes one breaking change and several enhancements:

- **HTTPS Required (Breaking Change)**: The SDK now enforces HTTPS URLs for `base_url`. If you were using HTTP URLs (e.g., for local testing), you will need to update to HTTPS. Note that the official DevRev API only supports HTTPS, so this should not affect production usage.
- **New Services**: 10 additional service classes are now available
- **Enhanced Error Messages**: More detailed error information is provided

All existing API calls remain compatible - only the HTTPS enforcement may require configuration changes for non-production environments.

## Reporting Issues

Found a bug or have a suggestion? Please [open an issue](https://github.com/mgmonteleone/py-dev-rev/issues/new).

