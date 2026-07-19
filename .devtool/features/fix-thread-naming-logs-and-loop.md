---
id: "fix-thread-naming-logs-and-loop"
status: "review"
priority: "high"
assignee: null
epic: null
dueDate: null
created: "2026-07-18T19:36:00.000Z"
modified: "2026-07-18T19:36:00.000Z"
completedAt: null
labels: []
order: "a10"
---
# Bug: Fix Thread Naming Infinite Loop and Remove Debug Logs

The GUI app has debug logs and a potential runaway infinite loop generating thread titles when it should not be.
- Stop generating thread titles/snippets if generation is disabled or if it runs repeatedly.
- Remove thread-naming debug logs that are flooding stdout/stderr.
