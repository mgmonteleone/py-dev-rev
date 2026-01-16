# Security and Secrets Management

## Critical Rule

**NEVER commit PII (Personally Identifiable Information) or secrets to code or repositories.**

## Secrets Management

### Environment Variables

- Store all secrets in environment variables
- Use `.env` files for local development ONLY
- **Always add `.env` to `.gitignore`** - verify this before any commit
- Use `python-dotenv` for loading environment variables in development
- Always use google secret manager for secrets, mounting secrets in ENV vars when on google application platforms.

### Configuration Pattern

```python
from pydantic import ConfigDict, SecretStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    api_key: SecretStr
    database_url: SecretStr
    debug: bool = False
```

### Secrets to Never Commit

- API keys and tokens
- Database connection strings
- Private keys and certificates
- OAuth client secrets
- Encryption keys
- Passwords and credentials
- AWS/GCP/Azure credentials
- Webhook secrets

## PII Protection

### Data to Protect

- Names, addresses, phone numbers
- Email addresses (in production data)
- Social Security Numbers, National IDs
- Financial information (credit cards, bank accounts)
- Health information
- Biometric data
- IP addresses (in some contexts)

### Protection Strategies

- Never use real PII in test fixtures or examples
- Use faker libraries for generating test data
- Implement data masking for logs
- Sanitize error messages before logging

## Pre-Commit Security Checks

### Required Checks Before Every Commit

1. **Scan for secrets**: Use tools like `detect-secrets` or `gitleaks`
2. **Review `.gitignore`**: Ensure sensitive files are excluded
3. **Check environment files**: Verify no `.env` files are staged
4. **Audit new dependencies**: Check for known vulnerabilities

### Tools Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

## Secure Coding Practices

- Use parameterized queries to prevent SQL injection
- Sanitize user input before processing
- Use secure random generation (`secrets` module, not `random`)
- Implement proper authentication and authorization
- Use HTTPS for all external communications
- Validate and sanitize all external data

## Logging Security

- Never log sensitive data (passwords, tokens, PII)
- Use structured logging with filtered fields
- Implement log levels appropriately
- Sanitize exception messages before logging

```python
import logging

# Bad - logs sensitive data
logger.info(f"User {user.email} logged in with token {token}")

# Good - logs only necessary info
logger.info(f"User {user.id} logged in successfully")
```

## Dependency Security

- Regularly run `pip-audit` or `safety` to check for vulnerabilities
- Keep dependencies updated to patch security issues
- Review security advisories for critical dependencies
- Use Dependabot or similar for automated security updates