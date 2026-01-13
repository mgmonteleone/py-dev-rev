# Changelog

All notable changes to the DevRev Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Documentation site with MkDocs Material theme
- Comprehensive API reference documentation
- Tutorials and guides for common use cases
- Example applications (basic, advanced, integrations)
- SECURITY.md with security policy and best practices
- Performance benchmarking framework
- Load testing support

### Changed
- Improved error messages with more context
- Enhanced logging with structured output

### Fixed
- Model validation for edge cases

### Security
- **HTTPS Enforcement**: Added validation to reject insecure HTTP URLs in `base_url` configuration
  - Prevents accidental credential leakage over unencrypted connections
  - Clear error messages guide users to use HTTPS
- Security audit completed with `bandit` (5,189 lines scanned, 0 issues)
- Dependency audit completed with `pip-audit` (0 known vulnerabilities)
- Added comprehensive security tests for token masking and URL validation
- Updated SECURITY.md with audit results and implementation details

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
| 0.1.0 | 2026-01-12 | Initial release with full API coverage |

## Upgrading

### From 0.x to 1.0

When 1.0 is released, migration guide will be added here.

## Reporting Issues

Found a bug or have a suggestion? Please [open an issue](https://github.com/mgmonteleone/py-dev-rev/issues/new).

