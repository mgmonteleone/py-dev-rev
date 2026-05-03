---
description: Start working on a GitHub or Linear issue using the Foreman agent
argument-hint: [issue-id-or-number]
model: prism-b
---

# Foreman Work Command

You are invoking the **Foreman** agent to work on a GitHub or Linear issue. The Foreman orchestrates complete feature development from issue analysis to PR creation while preserving the privacy boundary between public GitHub issues and private Linear issues.

## Arguments

- `$ARGUMENTS` - Optional GitHub issue number/URL or Linear issue identifier (e.g., `123`, `#123`, `https://github.com/.../issues/123`, or `CUSS-220`)

## Workflow

### If an issue identifier is provided:

Resolve and work on issue `$ARGUMENTS`:

1. Determine the issue source:
   - If `$ARGUMENTS` is a GitHub issue number (`123`, `#123`) or GitHub issue URL, fetch it using `gh issue view`, the GitHub API, or the GitHub MCP tools.
   - If `$ARGUMENTS` is a Linear identifier (`TEAM-123`, e.g. `CUSS-220`), fetch it from Linear.
   - If the identifier is ambiguous, try the most likely source first and ask the user only if both sources match or neither source matches.
2. If a GitHub issue is found, copy it to Linear before implementation:
   - Search Linear first for an existing issue that references the GitHub URL or `Source: GitHub #{number}` to avoid duplicate imports.
   - Create a Linear issue with the GitHub issue title, public issue body, GitHub URL, labels/milestone when useful, and a clear `Source: GitHub #{number}` note.
   - If an imported Linear issue already exists, reuse it as the primary tracking issue instead of creating a duplicate.
   - Treat the new Linear issue as the primary tracking issue for planning and progress updates.
   - Do **not** post private Linear details back to GitHub. Public GitHub comments must remain public-safe.
3. If a Linear issue is found, use it directly:
   - Do **not** copy Linear issue content to GitHub.
   - Keep private/internal context in Linear only.
4. Analyze the issue requirements and linked issues in the appropriate source system.
5. Create an implementation plan.
6. Create a feature branch following the naming convention: `feature/issue-{tracking-id}-{slug}` where `tracking-id` is the Linear identifier for Linear-origin or GitHub-imported work.
7. Coordinate builder agents to implement components in parallel where possible.
8. Run tests and ensure quality checks pass.
9. Create a PR when implementation is complete.
10. Hand off to `pr-review-boss` for the review lifecycle.

### If NO issue identifier is provided:

Help the user select an issue to work on:

1. Fetch open GitHub issues that are NOT in progress using:
   ```bash
   gh issue list --state open --json number,title,labels,milestone --limit 20
   ```

2. Fetch actionable Linear issues that are NOT completed, canceled, in progress, or WIP using the Linear tools.

3. Filter out issues in either source that have "in progress" or "wip" labels/states.

4. Present the user with a numbered list of available issues, clearly marking the source:
   ```
   Available Issues:
   
   1. GitHub #42 - Implement user authentication
   2. Linear CUSS-220 - Support API key authentication for MCP endpoints
   3. GitHub #35 - Fix pagination on dashboard
   4. Linear ENG-29 - Update API rate limiting
   
   Enter the number of the issue you want to work on (1-4), or type 'q' to quit:
   ```

5. Wait for user input to select an issue.

6. Once selected, proceed with the full foreman workflow for that issue. If the selected issue is from GitHub, find or create the Linear copy first and then work from the Linear issue.

## Technical Standards

Follow all standards defined in the foreman agent:
- Python 3.11+ with strict typing
- Pydantic v2 for data models
- Google-style docstrings
- Latest stable library versions
- SOC-2 security mindset (no PII in logs, secure defaults)

## Constraints

- **ALL** commits must reference the active tracking issue. For GitHub-origin work, reference both the Linear tracking issue and the public GitHub issue when practical.
- **NEVER** copy Linear issue content to GitHub or otherwise expose private Linear context in public GitHub comments, PRs, branches, or commit messages.
- **ALWAYS** copy public GitHub issues to Linear before implementation so internal work is tracked privately.
- **NEVER** introduce deprecated library versions
- **ALWAYS** verify library docs are current before using
- **HANDLE** errors explicitly - no silent failures
- **UPDATE** the task list as you work to track progress

## Related Agents

You may dispatch these sub-agents as needed:
- `sub-agent-builder` - For implementing specific components
- `sub-agent-tester` - For comprehensive test coverage
- `sub-agent-documentation` - For README/CHANGELOG updates

