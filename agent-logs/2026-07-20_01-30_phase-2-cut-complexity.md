# Phase 2: Cut Dead Complexity from Tauri Backend

## Goal
Remove unused code after Phase 1 module split. The plan specified 4 areas: spare engine pre-warming, elaborate pause/resume, execution staging/payload system, and hardcoded skills API. Also remove anything else unused that the Phase 1 audit exposed.

## User Feedback & Decisions
- User confirmed Phase 2 plan from prior session
- "I'd like you to just save a prompt for me" for Phase 3 bugs — don't fix them now, just write the feature file for later

## Changes Made

### types.rs (148 → 111 lines)
- Removed `ExecutionPayload`, `SkillItem`, `WorkspaceItem`, `WorkspacesConfig`, `BrowserContext`
- Removed `staged_payload` from `AppState`
- All were only used by dead command handlers

### pty.rs (630 → 456 lines)
- Removed `prepare_spare_engine_inner()` and all spare-engine logic from `spawn_fresh_engine()`
- Removed `find_agent_pid()`, `has_open_write_files()`, `has_active_network_traffic()`, `has_child_processes()` — only used by elaborate pause/resume safe-stop loop
- `spawn_fresh_engine()` simplified: no more spare session rename, just kills existing session and spawns fresh

### server.rs (402 → 311 lines)
- Removed `handle_skills_list()` with all 6 hardcoded skill entries
- Removed `handle_payload_execute()` with staging overlay window logic
- Removed routes `/api/skills/list` and `/api/payload/execute`
- Removed `ExecutionPayload`, `SkillItem` imports; removed `AppState` unused import

### session.rs (1,142 → 750 lines)
- Removed `initialize_project_session()` — never called from frontend
- Removed `toggle_process_pause()` elaborate loop: replaced 40-line `std::thread::spawn` loop with lsof checks with simple direct `kill -TSTP/-CONT` + emit
- Removed `get_staged_payload()`, `confirm_staged_execution()`, `get_recent_workspaces()`
- Removed `dispatch_to_gemini()` — opens a Gemini window via JXA, never called
- Removed `get_browser_context()` — Chrome Canary JXA integration, never used
- Removed `read_thread_notes_file()`, `write_thread_notes_file()` — Obsidian integration, never called
- Kept `get_quota()` (frontend calls it), `get_initial_project()` (frontend calls it), `create_new_project()`, `select_directory()`

### main.rs (299 → 283 lines)
- Removed `prepare_spare_engine` thin wrapper
- Removed from invoke_handler: `prepare_spare_engine`, `initialize_project_session`, `get_browser_context`, `dispatch_to_gemini`, `read_thread_notes_file`, `write_thread_notes_file`, `get_staged_payload`, `get_recent_workspaces`, `confirm_staged_execution`
- Removed `staged_payload` Arc from AppState construction

## What Worked
- Audit: every removed command confirmed NOT called by `main.ts` via `invoke()` (verified with grep)
- All 4 target areas cut; 8 additional unused commands discovered during audit and also cut
- Clean compile with zero warnings (only `block v0.1.6` deprecation from dependency, not our code)

## What Didn't Work / Known Issues
- The `simplify-tauri-backend-modules.md` feature file was auto-archived to `archived/` subdirectory — had to edit it there
- Auto-commit via `auto_commit.py` hit LiteLLM 400 error, used fallback message

## Architecture Notes
- `session.rs` is still 750 lines — the PTY session management commands (switch, write, resize, engine management) are tightly coupled and not easily splittable
- `threads.rs` at 1,107 lines is the largest module; could potentially split into scan/search/cache concerns
- Frontend (`main.ts` at 4,568 lines) needs its own refactoring pass
- Phase 3 bug fixes saved to `.devtool/features/fix-tauri-backend-bugs.md` for next session
