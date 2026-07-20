---
id: simplify-tauri-backend-modules
status: in-progress
priority: high
assignee: null
epic: null
dueDate: null
created: 2026-07-20T00:45:00-06:00
modified: 2026-07-20T00:45:00-06:00
completedAt: null
labels: [refactor, tauri, backend]
order: 1
---

# Simplify Tauri Backend: Split main.rs into Modules

Split the monolithic 3,188-line `tauri-gui/src-tauri/src/main.rs` into focused modules with zero behavior changes.

## Modules to Extract

1. **`pty.rs`** — PTY spawning, tmux session management, output reading threads (`spawn_single_pty`, `is_tmux_available`, `has_tmux_session`, `get_tmux_session_name`, `get_tmux_pane_pid`, `is_engine_running_proc`, `trigger_tmux_refresh`, `ensure_hermes_serve_running`, `ensure_engine_pty`, `ensure_mini_pty`)

2. **`threads.rs`** — Thread scanning, caching, chain resolution (`scan_brain_threads`, `get_child_to_parent_map`, `get_root_thread_id`, `get_thread_chain`, `get_cached_thread_info`, `detect_project_path`, `get_last_message_timestamp`, `parse_rfc3339_to_unix`, `is_leap_year`, thread scanning caches/statics)

3. **`server.rs`** — Axum HTTP routes (`spawn_axum_server`, `ws_handler`, `handle_socket`, `handle_sync`, `handle_commit`, `handle_gemini_sync`, `handle_skills_list`, `handle_payload_execute`, WsState + WS_STATE)

4. **`session.rs`** — ProjectSession management, engine switching (`ProjectSession` struct, `AppState` struct, `initialize_project_session`, `switch_active_project`, `close_project_session`, `write_to_pty`, `resize_pty`, `toggle_process_pause`, `spawn_fresh_engine`, `is_engine_running`)

5. **`main.rs`** — Just Tauri entrypoint + command registration + `create_new_project`, `select_directory`, `copy_tmux_selection`, `open_path`, `get_threads`, `delete_thread`, file read/write commands, `save/load_prompt_draft`, `open_devtools`, `get_quota`

## Constraints
- Zero behavior changes — this is pure code movement
- All existing tests must still pass (there may be none)
- Import paths must be correct for the module structure
- `cargo check` must succeed in the `src-tauri/` directory
