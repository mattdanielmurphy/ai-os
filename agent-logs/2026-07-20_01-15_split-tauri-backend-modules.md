## Goal
Split the monolithic 3,188-line `main.rs` in the Tauri backend into focused modules with zero behavior changes.

## User Feedback & Decisions
- User confirmed all features are essential (thread browser, terminal tabs, Hermes chat)
- User agreed to keep Tauri + Rust stack (not switch to Wails/Go/webview)
- Top frustrations: thread management, Hermes integration, crashes/instability
- User approved the 3-phase simplification plan (split modules → cut complexity → fix bugs)

## Changes Made
1. **`types.rs` (148 lines)** — All shared data structures extracted: `ProjectSession`, `AppState`, `Payload`, `SwitchResult`, `ThreadLog`, `ThreadSearchResult`, `CachedThreadInfo`, `WorkspacesConfig`, etc.
2. **`pty.rs` (630 lines)** — PTY spawning, tmux session management, process detection (`is_engine_running_proc`), Hermes serve daemon, spare engine pre-warming, process introspection (pause/resume helpers). Exports `spawn_single_pty`, `ensure_engine_pty`, `ensure_mini_pty`, `spawn_fresh_engine`, tmux helpers.
3. **`threads.rs` (1,107 lines)** — Thread scanning, caching (`CachedThreadInfo`), chain resolution (`get_root_thread_id`, `get_thread_chain`), project path detection, all `#[tauri::command]` functions: `get_project_threads`, `get_all_agy_threads`, `delete_thread`, `read_thread_log`, `file_exists`, `patch_thread_log_with_output`, `search_project_threads`.
4. **`server.rs` (402 lines)** — Axum HTTP server, WebSocket relay, route handlers for `/api/context/sync`, `/api/revision/commit`, `/api/gemini/sync`, `/api/skills/list`, `/api/payload/execute`.
5. **`session.rs` (1,142 lines)** — ProjectSession management, engine switching, PTY I/O, process pause/resume, misc commands (select_directory, create_new_project, copy_tmux_selection, open_path, save/load_prompt_draft, get_quota, get_browser_context, dispatch_to_gemini, thread notes, staged payload).
6. **`main.rs` (299 lines)** — Slim entrypoint: module declarations, floating window initialization script, global shortcut registration, Axum server spawn, state management, Tauri command registration.

## What Worked
- Clean compile with zero warnings on first successful run
- All 30 Tauri commands registered correctly from their respective modules
- `prepare_spare_engine` required a thin wrapper in `main.rs` due to Tauri command macro limitations (commands must be in the same crate root or re-exported)

## What Didn't Work / Known Issues
- Initial attempt had circular dependency (`pty.rs` referenced `session.rs`'s `ProjectSession`). Solved by creating `types.rs` as a dependency-free foundation.
- `GlobalShortcutManager` trait import was lost in the split — added back explicitly.
- `session.rs` still at 1,142 lines — largest module. Could potentially be split further into `session.rs` (pure session management) and `commands.rs` (misc utility commands).

## Architecture Notes
- Module dependency graph: `types` ← `pty` ← `session` ← `main`; `types` ← `threads` ← `main`; `types` ← `server` ← `main`
- No circular dependencies. `types.rs` is the root, containing only struct/enum definitions with no references to other modules.
- Frontend (`main.ts` at 4,568 lines) was not touched — that's its own refactoring task.
