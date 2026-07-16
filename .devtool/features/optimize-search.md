---
id: "optimize-search"
status: "review"
priority: "high"
assignee: null
epic: null
dueDate: null
created: "2026-07-16T08:00:00.000Z"
modified: "2026-07-16T08:00:00.000Z"
completedAt: null
labels: []
order: "a2"
---
# Optimize Thread Browser Search Performance

Address high latency when searching for short queries (like "mac") in the thread database.
- Improve full-text search matching speed.
- Optimize the SQL query to avoid heavy relevance score calculation across every record.
- Improve index utilization or query structure.
