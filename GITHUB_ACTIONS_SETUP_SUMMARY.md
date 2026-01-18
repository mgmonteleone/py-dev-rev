# GitHub Actions Setup - Summary

## What Was Configured

### 1. Updated CI Workflow (`.github/workflows/ci.yml`)

**Changes**:
- ✅ Split test execution into unit tests and integration tests
- ✅ Unit tests always run (no API token required)
- ✅ Integration tests run conditionally when `DEVREV_API_TOKEN` secret is available
- ✅ Coverage is collected from both test suites

**Behavior**:
```yaml
# Always runs
- Run tests (unit tests only)
  pytest -m "not integration"

# Runs only if DEVREV_API_TOKEN secret is set
- Run integration tests (if API token available)
  env: DEVREV_API_TOKEN: ${{ secrets.DEVREV_API_TOKEN }}
  pytest tests/integration/ -m integration
```

### 2. New Integration Tests Workflow (`.github/workflows/integration-tests.yml`)

**Triggers**:
- 🕐 **Scheduled**: Daily at 6 AM UTC
- 🔘 **Manual**: Via workflow_dispatch
- 📝 **Automatic**: On pushes to main that change source code

**Features**:
- ✅ Runs full integration test suite on Python 3.11, 3.12, 3.13
- ✅ Tests backwards compatibility
- ✅ Creates GitHub issue if tests fail (indicates API breaking change)
- ✅ Only runs if `DEVREV_API_TOKEN` secret is available

### 3. Setup Script (`scripts/setup-github-secrets.sh`)

**Features**:
- ✅ Checks GitHub CLI installation and authentication
- ✅ Reads API token from `.env` or prompts for manual entry
- ✅ Validates token format (basic JWT check)
- ✅ Sets GitHub secret `DEVREV_API_TOKEN`
- ✅ Verifies secret was created successfully

**Usage**:
```bash
./scripts/setup-github-secrets.sh
```

### 4. Documentation

**Created**:
- ✅ `GITHUB_INTEGRATION_SETUP.md` - Quick reference guide
- ✅ `docs/guides/github-actions-setup.md` - Comprehensive setup guide
- ✅ Updated `README.md` with GitHub Actions section

## Next Steps to Complete Setup

### Step 1: Add GitHub Secret

**Option A: Automated (Recommended)**
```bash
./scripts/setup-github-secrets.sh
```

**Option B: Manual with GitHub CLI**
```bash
gh secret set DEVREV_API_TOKEN --body "your-api-token-here"
```

**Option C: Manual via Web UI**
1. Go to https://github.com/mgmonteleone/py-dev-rev/settings/secrets/actions
2. Click "New repository secret"
3. Name: `DEVREV_API_TOKEN`
4. Value: Your DevRev API token
5. Click "Add secret"

### Step 2: Verify Setup

```bash
# Check secret is set
gh secret list | grep DEVREV_API_TOKEN

# Expected output:
# DEVREV_API_TOKEN  Updated 2026-01-18
```

### Step 3: Test Locally (Optional)

```bash
# Set token from .env
export DEVREV_API_TOKEN=$(grep DEVREV_API_TOKEN .env | cut -d'=' -f2-)

# Run integration tests
pytest tests/integration/ -v -m integration

# Expected: 22 tests should pass
```

### Step 4: Trigger CI

```bash
# Commit and push changes
git add .
git commit -m "ci: Configure GitHub Actions for integration tests"
git push origin main

# Watch the workflow run
gh run watch
```

## What Happens After Setup

### On Every Push/PR

1. **Linting** - Ruff checks code quality
2. **Type Checking** - Mypy validates types
3. **Unit Tests** - 316 tests run (always)
4. **Integration Tests** - 22 tests run (if secret is set)
5. **Coverage Upload** - Results sent to Codecov

### Daily at 6 AM UTC

1. **Integration Tests** - Full suite runs against real API
2. **Backwards Compatibility** - Verifies API hasn't changed
3. **Issue Creation** - Creates GitHub issue if tests fail

### Manual Trigger

You can manually trigger integration tests:
```bash
gh workflow run integration-tests.yml
```

## Security Considerations

### ✅ What's Secure

- Secrets are **encrypted** by GitHub
- Secrets are **not exposed** in logs
- Secrets are **not available** to forks (prevents malicious PRs)
- Integration tests use **read-only** operations only
- Token can be **rotated** without code changes

### ⚠️ Best Practices

1. **Use read-only tokens** for CI/CD
2. **Rotate tokens** every 90 days
3. **Monitor workflow runs** for suspicious activity
4. **Revoke tokens immediately** if compromised
5. **Never commit** tokens to `.env` files

## Troubleshooting

### Integration Tests Not Running

**Check**:
```bash
gh secret list | grep DEVREV_API_TOKEN
```

**Fix**:
```bash
./scripts/setup-github-secrets.sh
```

### Integration Tests Failing

**Possible Causes**:
- Token expired
- Token has insufficient permissions
- API breaking change

**Fix**:
1. Generate new token in DevRev dashboard
2. Update secret: `gh secret set DEVREV_API_TOKEN --body "new-token"`
3. Check DevRev API changelog for breaking changes

### Tests Skip in Fork PRs

**This is expected!** GitHub doesn't expose secrets to forks for security.

**Solution**: Tests will run when PR is merged to main.

## Files Modified/Created

### Modified
- ✅ `.github/workflows/ci.yml` - Added integration test step
- ✅ `README.md` - Added GitHub Actions setup section
- ✅ `pyproject.toml` - Pinned pytest <9.0.0 for compatibility

### Created
- ✅ `.github/workflows/integration-tests.yml` - Scheduled integration tests
- ✅ `scripts/setup-github-secrets.sh` - Automated setup script
- ✅ `GITHUB_INTEGRATION_SETUP.md` - Quick reference guide
- ✅ `docs/guides/github-actions-setup.md` - Comprehensive guide
- ✅ `GITHUB_ACTIONS_SETUP_SUMMARY.md` - This file

## Summary

✅ **GitHub Actions is now configured to run integration tests!**

**To complete setup, run**:
```bash
./scripts/setup-github-secrets.sh
```

**Then verify**:
```bash
gh secret list
git push origin main
gh run watch
```

---

**For detailed documentation**, see:
- Quick Reference: [GITHUB_INTEGRATION_SETUP.md](GITHUB_INTEGRATION_SETUP.md)
- Full Guide: [docs/guides/github-actions-setup.md](docs/guides/github-actions-setup.md)

