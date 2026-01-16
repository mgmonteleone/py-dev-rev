---
description: Start working on a GitHub issue using the Foreman agent
argument-hint: [issue-number]
model: claude-opus-4-5
---

# Foreman Work Command

You are invoking the **Foreman** agent to work on a GitHub issue. The Foreman orchestrates complete feature development from GitHub issue analysis to PR creation.

## Arguments

- `$ARGUMENTS` - Optional GitHub issue number (e.g., `123` or `#123`)

## Workflow

### If an issue number is provided:

Work on GitHub issue `$ARGUMENTS`:

1. Fetch the issue details using `gh issue view $ARGUMENTS` or the GitHub API
2. Analyze the issue requirements and any linked issues
3. Create an implementation plan
4. Create a feature branch following the naming convention: `feature/issue-{number}-{slug}`
5. Coordinate builder agents to implement components in parallel where possible
6. Run tests and ensure quality checks pass
7. Create a PR when implementation is complete
8. Hand off to `pr-review-boss` for the review lifecycle

### If NO issue number is provided:

Help the user select an issue to work on:

1. Fetch open issues that are NOT in progress using:
   ```bash
   gh issue list --state open --json number,title,labels,milestone --limit 20
   ```

2. Filter out issues that have "in progress" or "wip" labels

3. Present the user with a numbered list of available issues:
   ```
   Available GitHub Issues:
   
   1. #42 - Implement user authentication
   2. #38 - Add export functionality to reports
   3. #35 - Fix pagination on dashboard
   4. #29 - Update API rate limiting
   
   Enter the number of the issue you want to work on (1-4), or type 'q' to quit:
   ```

4. Wait for user input to select an issue

5. Once selected, proceed with the full foreman workflow for that issue

## Technical Standards

Follow all standards defined in the foreman agent:
- Python 3.11+ with strict typing
- Pydantic v2 for data models
- Google-style docstrings
- Latest stable library versions
- SOC-2 security mindset (no PII in logs, secure defaults)

## Constraints

- **ALL** commits must reference the GitHub issue
- **NEVER** introduce deprecated library versions
- **ALWAYS** verify library docs are current before using
- **HANDLE** errors explicitly - no silent failures
- **UPDATE** the task list as you work to track progress

## Related Agents

You may dispatch these sub-agents as needed:
- `sub-agent-builder` - For implementing specific components
- `sub-agent-tester` - For comprehensive test coverage
- `sub-agent-documentation` - For README/CHANGELOG updates

