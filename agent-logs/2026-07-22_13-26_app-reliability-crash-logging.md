## Goal
Fix app crashing, freezing, quick prompt context issues, defer background thread loading, and add crash logging.

## User Feedback & Decisions
- Defer background coding thread gathering until Coding window is spawned/visible.
- Produce detailed crash logs on disk for panics/crashes.
- Fix Quick Prompt window freezing when pasting context.

## Changes Made
- `tauri-gui/src-tauri/src/main.rs`: Added `std::panic::set_hook` to log Rust backtraces to `~/.ai-os/crash_logs/crash_<timestamp>.log`.
- `tauri-gui/src/main.ts`: Deferred initial `syncProjectsFromAllThreads()` call on startup and guarded periodic sync with `appWindow.isVisible()`.
- `tauri-gui/src/floating.ts`: Removed dead `dispatch_to_gemini` call to prevent JS exceptions on Enter.
- `userscripts/gemini.js`: Updated context pill injection to mark contexts inactive before DOM insertion, preventing recursive mutation observer loops.

## What Worked
- `bun --cwd tauri-gui build` succeeded with zero TypeScript/Vite errors.
- `cargo check --manifest-path tauri-gui/src-tauri/Cargo.toml` compiled cleanly.

## Architecture Notes
- Heavy thread scanning and JSON parsing should never run while only the Gemini or Quick Prompt windows are active.
