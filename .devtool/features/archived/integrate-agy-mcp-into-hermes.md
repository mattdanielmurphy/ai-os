---
id: "integrate-agy-mcp-into-hermes"
status: "done"
priority: "medium"
assignee: null
epic: null
dueDate: null
created: "2026-07-11T16:21:00-06:00"
modified: "2026-07-12T05:32:25.958Z"
completedAt: "2026-07-12T05:32:25.958Z"
labels: []
order: "aD"
---
# Integrate agy-mcp into Hermes

Integrate the `agy-mcp` server into Hermes by:
1. Registering the server in the Hermes MCP configuration.
2. Creating a tmux launch agent wrapper plist and script following the tmux launch agent protocol.
3. Loading the agent via launchctl.
4. End-to-end validation using `agy_doctor`.