# Git Workflow and Versioning Standards

## Commit Practices

### Commit Frequently with Logical Progress

- **Commit as you make logical progress** on your work
- Each commit should represent a single logical change
- Keep commits small and focused
- Never commit broken or untested code to main branches

### Commit Message Format

Use comprehensive commit messages following conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring (no feature or fix)
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependency updates
- `ci`: CI/CD configuration changes

#### Examples

```
feat(auth): add OAuth2 authentication support

Implement OAuth2 flow with support for Google and GitHub providers.
Includes token refresh handling and secure session management.

Closes #123
```

```
fix(api): handle rate limiting errors gracefully

Add exponential backoff retry logic when API returns 429 status.
Maximum 3 retries with 1s, 2s, 4s delays.

Fixes #456
```

## Semantic Versioning

### Version Format: MAJOR.MINOR.PATCH

**Always tag commits with appropriate semantic version tags.**

### When to Increment

#### MAJOR (X.0.0)
Increment for breaking changes:
- Removing or renaming public API endpoints
- Changing function signatures incompatibly
- Removing deprecated features
- Breaking changes to data models
- Major architectural changes

#### MINOR (0.X.0)
Increment for new features:
- Adding new endpoints or functions
- Adding optional parameters
- New functionality that is backwards-compatible
- Deprecating features (without removing)

#### PATCH (0.0.X)
Increment for bug fixes:
- Bug fixes
- Security patches
- Performance improvements (non-breaking)
- Documentation updates
- Dependency updates (non-breaking)

### Tagging Workflow

```bash
# After committing changes
git tag -a v1.2.3 -m "Release version 1.2.3: Brief description"
git push origin v1.2.3
```

### Pre-release Versions

For development/testing releases:
- Alpha: `v1.0.0-alpha.1`
- Beta: `v1.0.0-beta.1`
- Release Candidate: `v1.0.0-rc.1`

## Branch Strategy

### Main Branches

- `main`: Production-ready code, always stable
- `develop`: Integration branch for features (if using GitFlow)

### Feature Branches

- Prefix: `feature/` (e.g., `feature/add-user-auth`)
- Branch from: `main` or `develop`
- Merge via: Pull Request

### Bugfix Branches

- Prefix: `fix/` (e.g., `fix/login-error`)
- For hotfixes: `hotfix/` (e.g., `hotfix/security-patch`)

### Release Branches

- Prefix: `release/` (e.g., `release/v1.2.0`)
- Used for release preparation and final testing

## Pre-Commit Checklist

Before every commit, verify:

1. [ ] All tests pass
2. [ ] No linting errors (ruff, flake8)
3. [ ] No secrets or PII in code
4. [ ] Commit message follows conventions
5. [ ] Version tag applied (for releases)

## Version File Management

Update version in `pyproject.toml`:

```toml
[project]
version = "1.2.3"
```

Consider using `bump2version` or similar tools for automated version management.