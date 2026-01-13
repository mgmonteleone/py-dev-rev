---
type: "agent_requested"
description: "Example description"
---

# Pull Request and Code Review Standards

## When to Create Pull Requests

**Create PRs before committing MINOR and MAJOR version changes.**

| Version Change | PR Required | Review Required |
|----------------|-------------|-----------------|
| PATCH (0.0.X)  | Optional    | Optional        |
| MINOR (0.X.0)  | **Required**| Human + AI      |
| MAJOR (X.0.0)  | **Required**| Human + AI      |

## PR Creation Workflow

### 1. Pre-PR Checklist

Before creating a PR, verify:

- [ ] All tests pass: `pytest`
- [ ] Code quality checks pass: `ruff check . && flake8 .`
- [ ] Code is formatted: `ruff format .`
- [ ] No secrets or PII in code
- [ ] Documentation is updated
- [ ] Version is bumped appropriately
- [ ] CHANGELOG is updated (for MINOR/MAJOR)

### 2. Branch Preparation

```bash
# Ensure branch is up to date with main
git fetch origin
git rebase origin/main

# Verify all checks pass
pytest
ruff check .
```

### 3. PR Title Format

Follow conventional commit format:

```
<type>(<scope>): <description>
```

Examples:
- `feat(auth): add OAuth2 authentication support`
- `fix(api): handle rate limiting errors gracefully`
- `refactor(models): consolidate user data models`

### 4. PR Description Template

```markdown
## Summary

Brief description of what this PR does and why.

## Changes

- List of specific changes made
- Breaking changes (if any)
- New dependencies added

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Screenshots (if applicable)

## Checklist

- [ ] Tests pass
- [ ] Linting passes
- [ ] Documentation updated
- [ ] Version bumped
- [ ] No secrets committed
```

## Review Process

### Human Review

Human reviewers should verify:

1. **Business Logic**: Does the code do what it's supposed to?
2. **Architecture**: Does this fit well with existing patterns?
3. **Security**: Are there any security concerns?
4. **User Impact**: How does this affect end users?

### AI Review

AI reviewers should verify:

1. **Code Quality**: Follows project standards
2. **Test Coverage**: Adequate tests for new functionality
3. **Documentation**: Clear and complete
4. **Best Practices**: OOP principles, DRY, SOLID
5. **Dependencies**: Latest stable versions used

## PR Review Checklist

### For Reviewers

- [ ] Code follows project style guidelines
- [ ] No obvious bugs or logic errors
- [ ] Error handling is appropriate
- [ ] No security vulnerabilities introduced
- [ ] Tests are meaningful (not trivially passing)
- [ ] Documentation is clear and accurate
- [ ] No unnecessary complexity
- [ ] Breaking changes are documented

### Common Review Feedback

When reviewing, look for:

- Unused imports or variables
- Missing type hints
- Inadequate error handling
- Hardcoded values that should be configurable
- Missing or weak tests
- Performance concerns
- Security issues (SQL injection, XSS, etc.)

## Merging Strategy

### Merge Requirements

- At least 1 human approval
- All CI checks pass
- No unresolved conversations
- Branch is up to date with target

### Merge Method

- **Squash and merge**: For feature branches (clean history)
- **Merge commit**: For release branches (preserve history)
- **Rebase and merge**: When linear history is preferred

## Post-Merge Actions

After PR is merged:

1. Delete the feature branch
2. Tag the release (for version bumps)
3. Deploy if applicable
4. Update related issues/tickets

```bash
# Tag after merge (on main branch)
git checkout main
git pull origin main
git tag -a v1.2.0 -m "Release v1.2.0: Feature description"
git push origin v1.2.0
```

## Handling PR Feedback

When feedback is received:

1. Respond to all comments
2. Make requested changes
3. Re-request review after updates
4. Don't force-push after review has started (unless agreed)

## Emergency Hotfixes

For critical production issues:

1. Create `hotfix/` branch from main
2. Minimal changes only
3. Fast-track review (single approval)
4. Merge and tag as PATCH version
5. Create follow-up PR for comprehensive fix if needed