---
id: "stable-anchor-context-strategy"
status: "review"
priority: "high"
assignee: null
epic: null
dueDate: null
created: "2026-07-08T00:37:00.000Z"
modified: "2026-07-09T20:47:33.633Z"
completedAt: null
labels: []
order: "aB"
---
# Stable Anchor Context Strategy

This feature involves designing and implementing the **Stable Anchor + Volatile Append** strategy for workspace/codebase context orchestration.

### Reference Documentation
See the detailed architectural concept in [stable-anchor-context-strategy.md](file:///Users/matt/projects/ai-os/docs/stable-anchor-context-strategy.md).

### Next Steps & Strategy Considerations
- Investigate lightweight `ctags` parsing options to dynamically build the stable repo map.
- Strategize integration of the generator script into the current launchd/git-sync workflow.
- Standardize the prompt-appending pipeline order to structure system instructions, repo map, active files, and user task.