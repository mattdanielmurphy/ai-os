---
id: "three-turn-delegation-protocol"
status: "review"
priority: "medium"
assignee: null
epic: null
dueDate: null
created: "2026-07-10T12:01:00Z"
modified: "2026-07-10T12:01:00Z"
completedAt: null
labels: []
order: "aB"
---
# Three-Turn Delegation Protocol

Implement a structured 3-turn delegation system in Orchestrator-Only Mode (Mode 3):
1. Turn 1 (Recon/Retrieval): Process prompt, determine grep/file retrieval targets, and delegate the recon/retrieval phase to a cheap model (via Claude Code subagent).
2. Turn 2 (Decision/Planning & Action): The retrieved context is analyzed by the orchestrator, who makes a decision/implementation plan and delegates tasks to cheap subagents (Claude Code/mechanical_editor).
3. Turn 3 (Verification & Correction): Orchestrator inspects the diffs/build status, and delegates any necessary corrections to subagents.
Update workspace rules in `.agents/AGENTS.md` and `AGENTS.md` to document and enforce this workflow.