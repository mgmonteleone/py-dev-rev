---
description: Simplify and refine code for clarity, consistency, and maintainability
argument-hint: [file-path-or-scope]
model: claude-opus-4-5
---

# Simplify Code Command

You are invoking the **Code Simplifier** agent to analyze and refine code for clarity, consistency, and maintainability while preserving all functionality.

## Arguments

- `$ARGUMENTS` - Optional scope specification:
  - **File path**: Specific file to simplify (e.g., `src/services/job_service.py`)
  - **Directory path**: Directory to analyze (e.g., `src/services/`)
  - **"recent"**: Focus on recently modified files (default behavior)
  - **"staged"**: Focus on currently staged changes
  - **"pr"**: Focus on files changed in the current PR/branch

## Workflow

### If a specific file or directory is provided:

Simplify code in `$ARGUMENTS`:

1. Read the specified file(s) and understand the current implementation
2. Analyze for opportunities to improve clarity and consistency
3. Apply project-specific best practices from `.augment/rules/`
4. Make refinements that preserve exact functionality
5. Verify changes don't break tests
6. Report the simplifications made

### If "recent" or no argument is provided:

Focus on recently modified code:

1. Identify recently modified files using:
   ```bash
   git diff --name-only HEAD~5
   ```

2. Analyze each modified file for simplification opportunities

3. Apply refinements following project standards

4. Verify all tests still pass

### If "staged" is provided:

Focus on currently staged changes:

1. Get staged files:
   ```bash
   git diff --cached --name-only
   ```

2. Analyze only the staged portions of code

3. Apply refinements before commit

### If "pr" is provided:

Focus on PR changes:

1. Get files changed in current branch vs main:
   ```bash
   git diff --name-only main...HEAD
   ```

2. Analyze all changed files in the PR

3. Apply refinements to improve PR quality

## Simplification Priorities

Apply these refinements in order of impact:

1. **Remove dead code** - Unused imports, unreachable code, commented-out code
2. **Reduce nesting** - Flatten deeply nested conditionals with early returns
3. **Consolidate logic** - Merge related operations, eliminate redundancy
4. **Improve naming** - Use clear, descriptive variable and function names
5. **Apply Python idioms** - Use list comprehensions, context managers, etc.
6. **Enhance type hints** - Add or improve type annotations

## Technical Standards

Follow all Python standards defined in project rules:
- Python 3.11+ with modern syntax (`|` unions, `match` statements)
- Pydantic v2 for data models
- Google-style docstrings
- Strict type hints throughout
- No nested ternary operators - prefer explicit conditionals

## Constraints

- **NEVER** change what the code does - only how it does it
- **ALWAYS** run tests after making changes
- **PREFER** clarity over brevity - explicit is better than clever
- **AVOID** over-simplification that reduces maintainability
- **PRESERVE** helpful abstractions and documentation
- **VERIFY** no linting errors after changes (ruff, flake8, mypy)

## Output

After simplification, provide a summary:

```
📝 Code Simplification Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Files analyzed: 5
Files modified: 3
Simplifications applied: 12

Changes by category:
- Dead code removed: 4
- Nesting reduced: 3
- Logic consolidated: 2
- Naming improved: 2
- Type hints added: 1

Tests: ✅ All passing
Linting: ✅ No errors
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Related Agents

This agent works well after:
- `builder` - Simplify newly implemented components
- `bug-fixer` - Clean up after fixes are applied

This agent should run before:
- `tester` - Ensure clean code before adding tests
- `documentation` - Document simplified code

