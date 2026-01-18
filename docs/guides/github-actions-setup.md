# GitHub Actions Setup for Integration Tests

This guide explains how to configure GitHub Actions to run integration tests that require a DevRev API token.

## Overview

The SDK includes integration tests that make real API calls to verify compatibility with the DevRev API. These tests are:
- **Read-only** (safe, non-destructive)
- **Skipped by default** when no API token is available
- **Optional** for CI/CD pipelines

## Step 1: Create a DevRev API Token

1. Log in to your DevRev dashboard
2. Go to **Settings** → **API Keys**
3. Create a new API key with **read-only permissions**
4. Copy the token (you'll need it in the next step)

!!! warning "Security"
    Use a **read-only token** for CI/CD to minimize security risks.
    Never use a token with write permissions in automated workflows.

## Step 2: Add Token as GitHub Secret

### Via GitHub Web UI

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `DEVREV_API_TOKEN`
5. Value: Paste your API token
6. Click **Add secret**

### Via GitHub CLI

```bash
# Set the secret using GitHub CLI
gh secret set DEVREV_API_TOKEN --body "your-api-token-here"

# Verify it was added
gh secret list
```

## Step 3: Update CI Workflow

The CI workflow is already configured to use the secret. The integration tests will:
- ✅ Run when `DEVREV_API_TOKEN` secret is available
- ✅ Skip gracefully when the secret is not set
- ✅ Only execute read-only operations

### Current Configuration

The `.github/workflows/ci.yml` includes:

```yaml
- name: Run tests with integration tests
  env:
    DEVREV_API_TOKEN: ${{ secrets.DEVREV_API_TOKEN }}
  run: pytest --cov=src/devrev --cov-report=xml -v -m "not integration or (integration and api_token)"
```

This configuration:
- Sets the `DEVREV_API_TOKEN` environment variable from GitHub secrets
- Runs all unit tests
- Runs integration tests only if the token is available

## Step 4: Verify Setup

### Check Secret is Set

```bash
# List secrets (won't show values, just names)
gh secret list

# Expected output:
# DEVREV_API_TOKEN  Updated YYYY-MM-DD
```

### Test Locally

Before pushing, test the integration tests locally:

```bash
# Set your token
export DEVREV_API_TOKEN="your-token-here"

# Run integration tests
pytest tests/integration/ -v -m integration

# Expected: 22+ tests should pass
```

### Monitor CI Runs

After pushing, check the GitHub Actions tab:
- Unit tests should always pass
- Integration tests should pass if the secret is set
- Integration tests should skip if the secret is not set

## Security Best Practices

### ✅ DO

- Use **read-only API tokens** for CI/CD
- Store tokens in **GitHub Secrets** (encrypted)
- Use **repository secrets** for private repos
- Use **environment secrets** for additional protection
- Rotate tokens regularly
- Revoke tokens immediately if compromised

### ❌ DON'T

- Never commit tokens to `.env` files
- Never use tokens with write permissions in CI
- Never log token values in CI output
- Never share tokens across multiple projects
- Never use personal tokens for organization repos

## Troubleshooting

### Integration Tests Not Running

**Symptom**: Integration tests are skipped in CI

**Solution**: Verify the secret is set:
```bash
gh secret list | grep DEVREV_API_TOKEN
```

### Integration Tests Failing

**Symptom**: Tests fail with authentication errors

**Solutions**:
1. Verify token is valid (not expired)
2. Check token has correct permissions
3. Verify token is for the correct DevRev organization

### Secret Not Available in Forks

**Symptom**: Integration tests skip in pull requests from forks

**Explanation**: This is expected behavior. GitHub does not expose secrets to workflows triggered by forks for security reasons.

**Solution**: This is intentional and secure. Integration tests will run when the PR is merged to main.

## Advanced: Separate Integration Test Workflow

For more control, you can create a separate workflow for integration tests:

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
  workflow_dispatch:  # Manual trigger

jobs:
  integration:
    runs-on: ubuntu-latest
    if: ${{ secrets.DEVREV_API_TOKEN != '' }}
    
    steps:
      - uses: actions/checkout@v6
      
      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      
      - name: Run integration tests
        env:
          DEVREV_API_TOKEN: ${{ secrets.DEVREV_API_TOKEN }}
        run: pytest tests/integration/ -v -m integration
```

This workflow:
- Runs daily to catch API changes
- Can be triggered manually
- Only runs if the secret is available
- Focuses exclusively on integration tests

## Summary

✅ **Setup Complete** when:
1. GitHub secret `DEVREV_API_TOKEN` is set
2. CI workflow passes with integration tests
3. No token values appear in logs
4. Tests skip gracefully when token is missing

---

**Next Steps**: See [Testing Guide](testing.md) for more information on writing and running tests.

