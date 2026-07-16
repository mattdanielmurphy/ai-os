---
id: "fix-kanban-task-management"
status: "done"
priority: "medium"
assignee: null
epic: null
dueDate: null
created: "2026-07-09T17:55:00.000Z"
modified: "2026-07-12T05:32:25.854Z"
completedAt: "2026-07-12T05:32:25.854Z"
labels: []
order: "a7"
---
# Bug: Fix Kanban Feature Task Management

Fix issues with the agent's Kanban feature task management:
1. Do not ask for user approval when creating a feature file (no "please approve it").
2. Ensure created features do not have `title` or `description` in frontmatter. Instead, use a `# Title` header and markdown description in the body.
3. Keep finished features in `status: "review"` and leave them in `.devtool/features/` instead of marking them `done` or moving them to `.devtool/features/done/`.