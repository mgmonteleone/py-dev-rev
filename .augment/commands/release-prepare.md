---
description: Prepare and create a semantic versioned release with automated changelog
argument-hint: "[patch|minor|major]"
model: claude-opus-4-5
---

# Release Prepare Command

You are invoking the **Release Manager** agent to prepare and create a new release following semantic versioning.

## Arguments

- `$ARGUMENTS` - Optional version increment type: `patch`, `minor`, or `major`
  - If provided: Use the specified increment type
  - If omitted: Auto-determine based on commit history and PR labels

## Workflow

Execute these steps in exact order:

### Phase 1: Pre-Flight Checks

**All checks must pass before proceeding:**

```bash
# 1. Verify on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "ERROR: Must be on main branch. Currently on: $CURRENT_BRANCH"
    exit 1
fi

# 2. Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: Working directory has uncommitted changes"
    git status --short
    exit 1
fi

# 3. Fetch and verify synced with origin
git fetch origin main
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" != "$REMOTE" ]; then
    echo "ERROR: Local main is not synced with origin/main"
    echo "Local:  $LOCAL"
    echo "Remote: $REMOTE"
    echo "Run: git pull origin main"
    exit 1
fi

# 4. Verify CI checks passing
gh run list --branch main --limit 1 --json conclusion,status
```

### Phase 2: Version Analysis

```bash
# Get current version from pyproject.toml
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
echo "Current version: $CURRENT_VERSION"

# Get last release info
gh release list --limit 1 --json tagName,publishedAt,name

# Get commits since last release
LAST_TAG=$(gh release list --limit 1 --json tagName --jq '.[0].tagName')
git log ${LAST_TAG}..HEAD --pretty=format:"%h %s" --no-merges

# Get merged PRs since last release
LAST_DATE=$(gh release list --limit 1 --json publishedAt --jq '.[0].publishedAt')
gh pr list --state merged --search "merged:>=${LAST_DATE}" --json number,title,labels,body
```

**Version Increment Logic:**

If `$ARGUMENTS` is provided (patch/minor/major):
- Use the specified increment type

If `$ARGUMENTS` is empty, auto-determine:
1. Scan for `BREAKING CHANGE:` in commit messages → **MAJOR**
2. Scan for PRs with `breaking-change` or `major` labels → **MAJOR**
3. Scan for `feat:` or `feat(*)` prefixed commits → **MINOR**
4. Scan for PRs with `enhancement` or `feature` labels → **MINOR**
5. Otherwise → **PATCH**

### Phase 3: Calculate New Version

Parse current version and increment:
```
MAJOR.MINOR.PATCH
  |     |     |
  |     |     +-- Increment for patch
  |     +-------- Increment for minor (reset patch to 0)
  +-------------- Increment for major (reset minor and patch to 0)
```

### Phase 4: Update Version Files

**CRITICAL: Both files must be updated atomically:**

```bash
NEW_VERSION="X.Y.Z"  # Calculated version

# Update pyproject.toml
sed -i "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml

# Update __init__.py  
sed -i "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" src/jb_plugin_analyzer/__init__.py

# Verify both files match
TOML_VER=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
INIT_VER=$(grep '__version__' src/jb_plugin_analyzer/__init__.py | cut -d'"' -f2)
if [ "$TOML_VER" != "$INIT_VER" ]; then
    echo "ERROR: Version mismatch after update!"
    exit 1
fi

# Regenerate lock file
uv lock

# Verify lock file is in sync
uv lock --check
if [ $? -ne 0 ]; then
    echo "ERROR: Lock file verification failed"
    exit 1
fi
```

### Phase 5: Generate Release Notes

Build comprehensive release notes from:
1. Merged PR titles and descriptions
2. Closed GitHub issues referenced in PRs
3. Commit messages categorized by type

Format:
```markdown
## Release vX.Y.Z

### 🚨 Breaking Changes
<!-- Only if MAJOR increment -->

### ✨ New Features
- PR #123: Feature description
- PR #456: Another feature

### 🐛 Bug Fixes
- PR #789: Fix description

### 📚 Documentation
- Updated README, API docs

### 🔧 Maintenance
- Dependency updates, refactoring

### 📋 Issues Closed
- Closes #10, #20, #30

**Full Changelog**: compare/vOLD...vNEW
```

### Phase 6: Commit and Create Release

```bash
# Stage version files
git add pyproject.toml src/jb_plugin_analyzer/__init__.py uv.lock

# Commit
git commit -m "chore: bump version to $NEW_VERSION for release"

# Create annotated tag
git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"

# Push commit and tag (triggers CI/CD deployment)
git push origin main
git push origin "v$NEW_VERSION"

# Create GitHub release with generated notes
gh release create "v$NEW_VERSION" \
    --title "Release v$NEW_VERSION" \
    --notes "$RELEASE_NOTES"
```

### Phase 7: Deployment Confirmation

The tag push triggers `.github/workflows/deploy.yaml` which:
1. Builds Docker image with version tag
2. Deploys web service to Cloud Run
3. Deploys worker service to Cloud Run
4. Runs health checks

Monitor deployment:
```bash
gh run list --workflow=deploy.yaml --limit 1
```

## Output Format

Provide structured status at each phase:

```markdown
## 🚀 Release Preparation Status

### Pre-Flight Checks
- ✅ On main branch
- ✅ Working directory clean
- ✅ Synced with origin/main
- ✅ CI checks passing

### Version Analysis
- **Current Version**: 4.2.1
- **Last Release**: v4.2.1 (2026-01-15)
- **Changes Since**: 5 commits, 3 merged PRs
- **Increment Type**: MINOR (auto-detected: 2 feat: commits)
- **New Version**: 4.3.0

### Changes Included
| Type | Count | Details |
|------|-------|---------|
| Features | 2 | PR #205, #206 |
| Bug Fixes | 1 | PR #207 |
| Docs | 1 | PR #208 |

### Release Notes Preview
<!-- Show generated notes -->

### Deployment
- ✅ Tag v4.3.0 pushed
- ✅ GitHub Release created
- ⏳ Deployment workflow triggered
- 🔗 Monitor: https://github.com/.../actions/runs/...
```

## Error Handling

If any step fails:
1. Report the specific error clearly
2. Suggest remediation steps
3. Do NOT proceed with partial release
4. Rollback any changes if version files were modified:
   ```bash
   git checkout -- pyproject.toml src/jb_plugin_analyzer/__init__.py
   ```

## Constraints

- **REQUIRE** human confirmation before pushing tag and creating release
- **NEVER** proceed with failing pre-flight checks
- **ALWAYS** show release notes preview before creating release
- **VERIFY** deployment workflow started successfully

