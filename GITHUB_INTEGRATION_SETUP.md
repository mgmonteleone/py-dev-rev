# GitHub Integration Tests Setup

This document provides a quick reference for setting up GitHub Actions to run integration tests with the DevRev API.

## Quick Setup (Automated)

Use the provided script to automatically configure GitHub secrets:

```bash
./scripts/setup-github-secrets.sh
```

This script will:
1. ✅ Check if GitHub CLI is installed and authenticated
2. ✅ Read your API token from `.env` (or prompt for it)
3. ✅ Set the `DEVREV_API_TOKEN` GitHub secret
4. ✅ Verify the secret was created successfully

## Manual Setup

### Step 1: Add GitHub Secret

**Option A: Using GitHub CLI**
```bash
gh secret set DEVREV_API_TOKEN --body "your-api-token-here"
```

**Option B: Using GitHub Web UI**
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `DEVREV_API_TOKEN`
4. Value: Your DevRev API token
5. Click **Add secret**

### Step 2: Verify Secret

```bash
# List all secrets (won't show values)
gh secret list

# Expected output:
# DEVREV_API_TOKEN  Updated YYYY-MM-DD
```

## What Gets Configured

### 1. CI Workflow (`.github/workflows/ci.yml`)

**Runs on**: Every push and pull request

**Behavior**:
- ✅ Always runs unit tests (316 tests)
- ✅ Runs integration tests if `DEVREV_API_TOKEN` is available (22 tests)
- ✅ Skips integration tests gracefully if token is not set
- ✅ Uploads coverage to Codecov

### 2. Integration Tests Workflow (`.github/workflows/integration-tests.yml`)

**Runs on**:
- 🕐 Daily at 6 AM UTC (scheduled)
- 🔘 Manual trigger (workflow_dispatch)
- 📝 Pushes to main that change source code

**Behavior**:
- ✅ Runs full integration test suite
- ✅ Tests against real DevRev API
- ✅ Creates GitHub issue if tests fail (indicates API breaking change)
- ✅ Tests on Python 3.11, 3.12, and 3.13

## Integration Tests Overview

### What Tests Run

**Location**: `tests/integration/test_readonly_endpoints.py`

**Tests Include**:
- ✅ List accounts (read-only)
- ✅ List works (read-only)
- ✅ List tags (read-only)
- ✅ List parts (read-only)
- ✅ Authentication error handling
- ✅ Backwards compatibility checks

**All tests are READ-ONLY and safe!** No data is created, modified, or deleted.

### Test Markers

Tests use pytest markers for selective execution:

```python
@pytest.mark.integration  # Requires API token
@pytest.mark.asyncio      # Async test
```

Run specific test types:
```bash
# Only integration tests
pytest -m integration

# Only unit tests (no integration)
pytest -m "not integration"

# All tests
pytest
```

## Security Best Practices

### ✅ Token Security

- **Use read-only tokens** for CI/CD
- **Rotate tokens regularly** (every 90 days recommended)
- **Never commit tokens** to `.env` files
- **Use GitHub Secrets** for secure storage
- **Revoke immediately** if compromised

### ✅ CI/CD Security

- Secrets are **encrypted** by GitHub
- Secrets are **not exposed** in logs
- Secrets are **not available** to forks (security feature)
- Integration tests **skip gracefully** without token

## Troubleshooting

### Integration Tests Not Running

**Symptom**: Integration tests are skipped in CI

**Check**:
```bash
gh secret list | grep DEVREV_API_TOKEN
```

**Solution**: If not found, run setup script:
```bash
./scripts/setup-github-secrets.sh
```

### Integration Tests Failing

**Symptom**: Tests fail with authentication errors

**Possible Causes**:
1. Token expired
2. Token has insufficient permissions
3. Token is for wrong DevRev organization

**Solution**:
1. Generate new token in DevRev dashboard
2. Update GitHub secret:
   ```bash
   gh secret set DEVREV_API_TOKEN --body "new-token-here"
   ```

### Tests Skip in Pull Requests from Forks

**Symptom**: Integration tests skip in PRs from external contributors

**Explanation**: This is **expected and secure**. GitHub does not expose secrets to workflows triggered by forks.

**Solution**: Integration tests will run when PR is merged to main.

## Testing Locally

Before pushing, test integration tests locally:

```bash
# Set your token (from .env or manually)
export DEVREV_API_TOKEN="your-token-here"

# Run integration tests
pytest tests/integration/ -v -m integration

# Expected output:
# tests/integration/test_readonly_endpoints.py::test_list_accounts PASSED
# tests/integration/test_readonly_endpoints.py::test_list_works PASSED
# ... (22 tests total)
```

## Monitoring

### GitHub Actions Tab

Monitor test runs at:
```
https://github.com/mgmonteleone/py-dev-rev/actions
```

### Scheduled Runs

Integration tests run daily to catch API changes:
- **Time**: 6 AM UTC
- **Purpose**: Detect breaking changes in DevRev API
- **Action**: Creates GitHub issue if tests fail

### Coverage Reports

Coverage reports are uploaded to Codecov:
- **Unit tests**: ~81% coverage
- **Integration tests**: Additional real-world validation

## Summary

✅ **Setup is complete when**:
1. GitHub secret `DEVREV_API_TOKEN` is set
2. CI workflow shows integration tests running
3. No token values appear in logs
4. Tests pass or skip gracefully

---

**For detailed documentation**, see: [docs/guides/github-actions-setup.md](docs/guides/github-actions-setup.md)

