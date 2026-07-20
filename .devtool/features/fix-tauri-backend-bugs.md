---
id: fix-tauri-backend-bugs
status: review
priority: high
assignee: null
epic: simplify-tauri-backend-modules
dueDate: null
created: 2026-07-20T01:30:00-06:00
modified: 2026-07-20T13:38:00-06:00
completedAt: null
labels: [bug, tauri, backend]
order: 2
---

# Fix Tauri Backend Bugs

Fix the remaining reliability issues after Phase 1 (module split) and Phase 2 (dead code removal).

## Bugs to Fix

1. **Hermes WebSocket connection reliability**
   - WebSocket relay in `server.rs` occasionally drops or fails to reconnect
   - Investigate whether `WS_STATE` static + OnceLock is the right pattern
   - Ensure host/client registration survives transient disconnects

2. **Thread naming and grouping correctness**
   - Thread scanning in `threads.rs` may produce incorrect child-to-parent chains
   - Some threads show wrong project paths or missing titles
   - Verify `get_root_thread_id()` and chain resolution logic

3. **Terminal tab switching race conditions**
   - Rapid tab switching can leave stale PTY readers emitting to wrong tab
   - `switch_active_project` in `session.rs` may race with PTY output threads
   - Consider adding session-scoped output channels instead of global `emit_all`

## Context

- Backend now split into 5 modules: `types.rs` (111), `pty.rs` (456), `threads.rs` (1107), `server.rs` (311), `session.rs` (750), `main.rs` (283)
- Frontend (`main.ts`) is 4,568 lines — will likely need its own refactoring pass
