## Goal
Change the `ai-os` CLI tool to launch in GUI mode by default, passing the current working directory and auto-skipping permissions. Allow passing parameters to run in non-GUI (terminal) mode as it originally did.

## Changes Made
- **`bin/ai-os`**: 
  - Saved `$PWD` in `$ORIGINAL_PWD` before changing directories.
  - Switched the default of `LAUNCH_GUI` to `true`.
  - Added support for `--cli`, `--terminal`, and `--no-gui` options to force running non-GUI.
  - Exported `AIOS_INITIAL_PROJECT="$ORIGINAL_PWD"` when starting the GUI.
  - Changed CLI execution logic to `cd "$ORIGINAL_PWD"` before executing `claude` or `agy` with `--dangerously-skip-permissions`.
- **`src-tauri/src/main.rs`**:
  - Implemented the `get_initial_project` Tauri command, which reads the `AIOS_INITIAL_PROJECT` environment variable and returns it to the frontend.
  - Registered `get_initial_project` in the builder invoke handler.
- **`src/main.ts`**:
  - Added initial startup logic to retrieve the directory passed from CLI via `get_initial_project`.
  - If a directory is returned, automatically checks if it exists in the projects list; if not, appends it as a new project, saves, and sets it as the active workspace project.
  - Updated Claude startup command injection to also pass `--dangerously-skip-permissions` to align with the orchestrator.
- **`FEATURES.md`**: Documented Phase 5 features.
- **`AG_CONTEXT.md`**: Updated the Durable Knowledge Map.

## What Worked
- Vite and TypeScript compilations build without error.
- Rust Tauri backend compiles and checks clean.
- Setting `AIOS_INITIAL_PROJECT` in the shell wrapper and reading it in the frontend successfully bridges the terminal directory context to the GUI.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- Tauri environment variables can be fetched in Rust via `std::env::var("VAR_NAME")` and then queried asynchronously from the TypeScript frontend.
- Tmux sessions spawned by Tauri use `-c <project_path>` to ensure the shell process remains rooted in the project's actual path, keeping state clean.
