---
description: Start monitoring and reviewing PRs using the PR Review Boss agent
argument-hint: [check-interval-seconds] [duration-minutes]
model: claude-opus-4-5
---

# PR Review Start Command

You are invoking the **PR Review Boss** agent to monitor and process pull requests. This agent orchestrates the complete PR review lifecycle with parallel sub-agents.

## Arguments

- `$ARGUMENTS` - Optional parameters in format: `[check-interval-seconds] [duration-minutes]`
  - **check-interval-seconds**: How often to check for new PRs (default: 15 seconds)
  - **duration-minutes**: How long to keep monitoring (default: 120 minutes)

Parse the arguments:
- If one number provided: use as check interval, default duration to 120
- If two numbers provided: first is check interval, second is duration
- If no arguments: use defaults (15 seconds, 120 minutes)

## Workflow

### 1. Initial Setup

1. Parse the check interval and duration from `$ARGUMENTS`
2. Calculate the end time based on the duration
3. Log the monitoring parameters:
   ```
   🤖 PR Review Boss Starting
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Check Interval: 15 seconds
   Duration: 120 minutes
   End Time: [calculated end time]
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

### 2. Monitoring Loop

Repeat until the duration expires:

1. **Check for unprocessed PRs**:
   ```bash
   gh pr list --state open --json number,title,labels,author,createdAt --limit 20
   ```

2. **Filter PRs** - Skip PRs that:
   - Already have the `agent-reviewing` label
   - Are marked as draft
   - Were created by bots (unless they need review)

3. **If an unprocessed PR is found**:
   a. Add the `agent-reviewing` label to claim it:
      ```bash
      gh pr edit <number> --add-label "agent-reviewing"
      ```
   
   b. Process the PR through the full review lifecycle:
      - Fetch review comments from automated reviewers
      - Categorize issues by priority (CRITICAL, HIGH, MEDIUM, LOW)
      - Dispatch `sub-agent-bug-fixer` for issues (in parallel where independent)
      - Run `sub-agent-documentation` and `sub-agent-tester` in parallel
      - Request human approval before merging
      - Handle merge when approved
   
   c. Remove the `agent-reviewing` label when complete:
      ```bash
      gh pr edit <number> --remove-label "agent-reviewing"
      ```

4. **If no PRs to process**:
   - Log: `No new PRs to review. Checking again in {interval} seconds...`
   - Wait for the check interval before next iteration

5. **Check if duration has expired**:
   - If expired, log completion and exit
   - If not, continue monitoring loop

### 3. Completion

When the monitoring duration expires:
```
🤖 PR Review Boss Completed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Time: 120 minutes
PRs Processed: [count]
PRs Merged: [count]
Issues Fixed: [count]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Constraints

- **NEVER** merge a PR with failing GitHub Actions
- **ALWAYS** wait for explicit human approval before merging
- **ALL** commits must reference the PR number
- **USE** `--force-with-lease` for any force pushes after rebase
- **ENSURE** all related GitHub issues are updated and closed

## Error Handling

- If a sub-agent fails, log the error and continue with other agents
- If merge conflicts cannot be resolved, request human help
- If GitHub API calls fail, retry with exponential backoff (max 3 attempts)

## Related Agents

You will dispatch these sub-agents:
- `sub-agent-bug-fixer` - For resolving review comments and issues
- `sub-agent-documentation` - For updating docs based on PR changes
- `sub-agent-tester` - For adding missing test coverage

## Status Tracking

Use the `agent-reviewing` GitHub label to prevent race conditions:
- Add label when starting work on a PR
- Remove label when work is complete (merged or abandoned)
- Check for this label before claiming any PR

