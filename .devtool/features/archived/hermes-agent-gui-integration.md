---
id: "hermes-agent-gui-integration"
status: "review"
priority: "medium"
assignee: null
epic: null
dueDate: null
created: "2026-07-18T17:30:00.000Z"
modified: "2026-07-18T17:30:00.000Z"
completedAt: null
labels: []
order: "a3"
---
# Enable Hermes Agent Integration in Tauri GUI and Rename App Folder

Implement Hermes agent usage in the Tauri GUI instead of just Claude Code and agy.
1. When Hermes agent spins up an instance of agy via an MCP tool to make a subagent, use the backend to spawn a tmux TUI of agy, intercept the logs, and show the agy subagent that Hermes agent spins up in the thread as if it actually were Hermes agent. Switch the tmux to the TUI to steer it.
2. Leverage Hermes agent's robust ACP support to tap in easily and show the results in the webview threads.
3. Rename the app folder from `legacy-tauri-gui` to `tauri-gui` (removing "legacy") and update all workspace, script, and configuration references.
