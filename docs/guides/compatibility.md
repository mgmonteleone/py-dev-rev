# Version compatibility matrix

This page documents compatibility between SDK versions and Python versions.

## Python version compatibility

| SDK Version | Python 3.11 | Python 3.12 | Python 3.13 |
|-------------|-------------|-------------|-------------|
| v0.1.x      | ✓           | ✓           | ✓           |

## API compatibility

The SDK is generated from DevRev's public OpenAPI specification.

- The repository includes a pinned spec file: `openapi-public.yaml`
- Automation can open PRs when the spec changes.

## Dependency minimums

| Dependency | Minimum Version |
|------------|-----------------|
| httpx      | 0.25            |
| pydantic   | 2.5             |
