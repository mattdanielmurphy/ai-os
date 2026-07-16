---
id: "reduce-token-waste-patterns"
status: "done"
priority: "high"
assignee: null
epic: null
dueDate: null
created: "2026-07-10T08:00:00Z"
modified: "2026-07-12T05:32:26.016Z"
completedAt: "2026-07-12T05:32:26.016Z"
labels: []
order: "aH"
---
# Reduce Token Waste Patterns

Implement fixes for four token waste patterns identified in the audit:

1. **Async polling overhead** — mechanical_editor.py was launched async then polled with command_status, wasting ~3,000 tokens.
2. **Redundant git diff calls** — up to 6 git diff/status calls per conversation, many returning empty.
3. **SYSTEM_MESSAGE injection of subagent results** — subagent responses are huge blocks that permanently inflate context.
4. **Serial subagent trips** — asking subagents 1 question at a time instead of batching.

Changes:
- Strengthened Rule 12 (Synchronous Subagents) in AGENTS.md
- Added Rule 17 (Single Verification), Rule 18 (Batch Delegation), and Rule 19 (Concise Subagent Responses) to AGENTS.md
- Added --brief flag to research_agent.py supporting 500-token capped responses
- Verified mechanical_editor.py is already synchronous (no async/background pattern present)
- Updated FEATURES.md with Token Waste Reduction entry