## Goal
Fix nested execution in Tauri UI by improving engine running detection when inside tmux, and add an Auto-Clear checkbox to the prompt UI that persists state and updates the input placeholder.

## Changes Made
- **src-tauri/src/main.rs**:
  - Added `is_pid_alive` helper using standard POSIX `kill -0 <pid>` command execution.
  - Added `is_session_alive` helper to check tmux session existence (if tmux is available) or raw process status.
  - Updated `is_engine_running` and `ensure_engine_pty` to use `is_session_alive` so they correctly identify active tmux-hosted sessions.
- **index.html**:
  - Added an `Auto-Clear (/clear)` checkbox to the breadcrumb folder display area.
- **src/main.ts**:
  - Updated prompt submission handler to respect the checkbox checked state.
  - Added checkbox state initialization, `localStorage` persistence, and dynamic textarea placeholder updates.
- **FEATURES.md**:
  - Documented features and bug fixes.

## What Worked
- TMUX session-based checks correctly identify when Claude/Agy are running inside interactive PTY sessions, preventing the client from sending CLI strings to an open interactive shell.
- Checkbox successfully prevents `/clear` command generation and updates prompt placeholder.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- The Tauri PTY session architecture wraps engine execution inside tmux sessions named `ai_os_<engine>_<sanitized_path>`. Because the child commands run under the tmux server daemon rather than the client process, standard process tree parent-child checks failed to trace the engine execution correctly. Relying on `tmux has-session -t` solves this.
