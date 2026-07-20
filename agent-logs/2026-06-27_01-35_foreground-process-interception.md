## Goal
Prevent `ai-os` from nested-spawning `agy` (or `claude`) commands if the target CLI process is already running interactively in the foreground of the PTY shell.

## Changes Made
* **`src-tauri/src/main.rs`**:
  - Saved the PTY shell PID (`shell_pid`) inside the `AppState` struct on app startup.
  - Implemented the `is_engine_running` Tauri command. It runs `ps -A -o ppid,pid,args` to traverse the process list and checks recursively (via BFS) if any active descendant process under the shell's PID contains the name of the target engine (e.g. `agy` or `claude`).
  - Registered `is_engine_running` in the Tauri invoke handler.
* **`src/main.ts`**:
  - Updated the textarea `keydown` Enter listener. Before formulating a new command wrapper like `agy --add-dir=$PWD -i "..." --dangerously-skip-permissions` or `claude -p "..."`, we invoke `is_engine_running`.
  - If the engine is already running, we write the raw user input directly to the PTY stdin (`processedInput.replace(/\n/g, '\r') + '\r'`) instead of wrapping it as a new nested command, and skip the `/clear` command delay and sequential cost telemetry scripts.
* **`FEATURES.md`**:
  - Documented the new foreground process interception feature.

## What Worked
* `is_engine_running` successfully compiles and checks the descendant process tree.
* Frontend routing successfully intercepts the command and sends direct raw input if the process is already running.

## What Didn't Work / Known Issues
* None detected.

## Architecture Notes
* Storing the shell PID on startup is sufficient since `ai-os` runs a single persistent shell session.
* BFS traversal ensures that wrapper shell scripts, `node` processes, or other intermediate sub-processes running the target engine are correctly matched.
