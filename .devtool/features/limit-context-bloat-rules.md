---
id: "limit-context-bloat-rules"
status: "review"
priority: "medium"
assignee: null
epic: null
dueDate: null
created: "2026-07-10T18:05:50.000Z"
modified: "2026-07-10T18:05:50.000Z"
completedAt: null
labels: []
order: "aC"
---
# Limit Context Bloat Rules

Propose and enforce the following rules to limit context bloat and prevent 1M+ token conversations in the future:
1. Strict Output Truncation: Cap grep_search and run_command outputs returned to the orchestrator to a maximum of 1,000 tokens unless explicitly requested.
2. Early Thread Branching: Enforce a rule that if a conversation exceeds 15-20 steps, the orchestrator must branch to a fresh thread or subagent conversation rather than continuing to accumulate context history.
3. Optimized Grep Patterns: Require narrower directory searches (e.g., specifying file extensions or subdirectory paths) to prevent massive result lists.