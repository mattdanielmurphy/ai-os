---
id: fix-cmd-opt-m-minimization
status: "review"
priority: "high"
assignee: null
epic: null
dueDate: null
created: "2026-07-24T23:42:00-06:00"
modified: "2026-07-25T00:35:00-06:00"
completedAt: null
labels: ["bug", "tauri", "eventtap", "macos"]
order: 1
---

# Bug: Fix Cmd+Opt+M Window Minimization & CGEventTap Scope

Fix issue where Cmd+Opt+M minimizes the app window due to CGEventTap silent failure and native miniaturization.

1. Disable Native Window Minimization (`minimizable: false`) in Tauri config or WindowBuilder.
2. Register `Cmd+Option+M` via `tauri-plugin-global-shortcut` (Rust + JS/TS).
3. Narrow `CGEventTap` scope in `eventtap.rs` to only swallow QWERTY note keys when MIDI mode is active and remove Cmd+Opt+M swallowing logic from eventtap.
