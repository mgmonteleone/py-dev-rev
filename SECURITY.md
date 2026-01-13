# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in the DevRev Python SDK, please report it responsibly.

### How to Report

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. Email security concerns to: matthewm@augmentcode.com
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 48 hours of your report
- **Initial Assessment**: Within 5 business days
- **Resolution Timeline**: Critical issues within 7 days, others within 30 days
- **Credit**: We'll acknowledge your contribution in the release notes (unless you prefer anonymity)

## Security Best Practices

When using the DevRev Python SDK, follow these security guidelines:

### API Token Management

```python
# ✅ GOOD: Use environment variables
import os
from devrev import DevRevClient

client = DevRevClient()  # Reads DEVREV_API_TOKEN from env

# ✅ GOOD: Use secret management
from devrev import DevRevClient
token = get_secret_from_vault("devrev-api-token")  # Your secret manager
client = DevRevClient(api_token=token)

# ❌ BAD: Never hardcode tokens
client = DevRevClient(api_token="your-actual-token")  # NEVER DO THIS
```

### Secure Configuration

```python
# ✅ GOOD: Use .env files for local development (never commit!)
# .env file:
# DEVREV_API_TOKEN=your-token-here

# ✅ GOOD: Use environment-specific configs
from devrev import DevRevConfig

config = DevRevConfig(
    # Token from environment
    api_token=os.environ["DEVREV_API_TOKEN"],
    # Timeout to prevent hanging requests
    timeout=30,
    # Limit retries
    max_retries=3,
)
```

### Logging Security

The SDK is designed to never log sensitive data:

- ✅ API tokens are masked in logs
- ✅ Request/response bodies are not logged at INFO level
- ✅ Sensitive headers are redacted

```python
# Safe logging configuration
import logging
logging.getLogger("devrev").setLevel(logging.INFO)

# For debugging (use only in development!)
logging.getLogger("devrev").setLevel(logging.DEBUG)
```

### Input Validation

All inputs are validated using Pydantic:

```python
from devrev.models import WorksCreateRequest
from pydantic import ValidationError

try:
    # Input is validated before API call
    request = WorksCreateRequest(
        type="ticket",
        title="x" * 300,  # Too long - will fail validation
        applies_to_part="don:core:..."
    )
except ValidationError as e:
    print(f"Invalid input: {e}")
```

## Security Checklist

### Before Production Deployment

- [ ] API tokens stored in secure secret management (not in code)
- [ ] Environment variables used for configuration
- [ ] `.env` files excluded from version control
- [ ] Appropriate log level set (INFO or WARN in production)
- [ ] Timeout values configured appropriately
- [ ] Error handling in place (no stack traces exposed to users)
- [ ] Dependencies audited for vulnerabilities (`pip-audit`)

### Ongoing Security

- [ ] Regularly rotate API tokens
- [ ] Monitor for unusual API activity
- [ ] Keep SDK updated to latest version
- [ ] Review dependency updates for security patches

## Dependency Security

We regularly audit dependencies:

```bash
# Check for vulnerable dependencies
pip-audit

# Check code for security issues
bandit -r src/
```

### Current Security Status

| Tool | Last Run | Result |
|------|----------|--------|
| `bandit` | 2026-01-13 | ✅ No issues found (5,189 lines scanned) |
| `pip-audit` | 2026-01-13 | ✅ No known vulnerabilities |

### Audit Summary

- ✅ All dependencies audited and up-to-date
- ✅ No known vulnerabilities in SDK dependencies
- ✅ Code scanned with bandit (no issues at any severity)
- ✅ HTTPS enforcement implemented and tested
- ✅ API tokens protected with Pydantic SecretStr

## Secure Development

This SDK follows secure development practices:

1. **No Dynamic Code Execution** - No `eval()` or `exec()` calls
2. **Input Validation** - All inputs validated via Pydantic
3. **HTTPS Enforcement** - HTTP URLs are rejected at configuration time with a clear error message
4. **Certificate Validation** - SSL certificates are verified by default (httpx default behavior)
5. **Minimal Dependencies** - Only essential, well-maintained packages (pydantic, httpx, python-dotenv)
6. **Secret Protection** - API tokens stored as `SecretStr`, never logged or exposed in errors

## Security Features

### Built-in Protections

| Feature | Description | Implementation |
|---------|-------------|----------------|
| Token Masking | API tokens are never logged in full | Pydantic `SecretStr` type |
| HTTPS Enforcement | HTTP URLs are rejected at configuration | `field_validator` on `base_url` |
| Certificate Validation | SSL certificates are verified by default | httpx default behavior |
| Input Validation | All inputs validated before API calls | Pydantic models with strict typing |
| Rate Limit Handling | Respects `Retry-After` headers | `RateLimitError` with retry info |
| Timeout Protection | Configurable request timeouts | Default 30s, max 300s |

### Error Handling

Exceptions never expose sensitive information:

```python
from devrev.exceptions import AuthenticationError

try:
    client = DevRevClient()
    # ...
except AuthenticationError as e:
    # Safe to log - no token exposed
    logger.error(f"Auth failed: {e.message}")
```

### HTTPS Enforcement Example

```python
from devrev import DevRevClient, DevRevConfig
from pydantic import ValidationError

# This will raise ValidationError:
try:
    config = DevRevConfig(
        api_token="your-token",
        base_url="http://api.devrev.ai"  # HTTP not allowed!
    )
except ValidationError as e:
    print("Security: HTTP URLs are not allowed")
    # ValidationError: Insecure HTTP URLs are not allowed.
    # Use HTTPS to protect your API credentials.
```

## Contact

For security concerns: matthewm@augmentcode.com

For general support: https://github.com/mgmonteleone/py-dev-rev/issues

