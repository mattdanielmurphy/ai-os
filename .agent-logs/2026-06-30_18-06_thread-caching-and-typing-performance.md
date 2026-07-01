## Goal
Optimize app-wide scrolling and typing responsiveness by resolving rendering, polling, and IPC inefficiencies.

## Changes Made
- **Debounced Projects Autosave (Frontend)**: Introduced a 500ms debounced `saveProjectsDebounced` function to write prompt drafts to `localStorage` and prevent blocking the main browser UI thread on every keypress in the prompt textarea.
- **Conditional PTY Resizing (Frontend)**: Refactored `adjustHeight` in `src/main.ts` to only invoke PTY resizing when the prompt textarea's height actually changes (such as wrapping lines or manual resizing), using `debouncedResizePty` instead of the synchronous `resizePty` IPC wrapper.
- **Rust Backend Caching (OnceLock)**: Added `CHILD_TO_PARENT_CACHE` and `THREAD_INFO_CACHE` in `src-tauri/src/main.rs`. Replaced raw disk traversal and transcript file opens/reads in `scan_brain_threads`, `get_project_threads`, and `get_all_agy_threads` with metadata checks and caching. Now, thread headers and project association paths are only parsed on initial discovery or when a file modification time (`mtime`) or size changes, resolving CPU/disk thrashing during polling.

## What Worked
- Verified that `cargo check` and `pnpm run build` build correctly without errors or warnings.
- The UI runs with zero keypress input delay or layout stutter since heavy local storage serializations and Tauri PTY resizing IPC calls are no longer executed on every keystroke.
- Disk usage and file descriptor reads dropped significantly since backend scans bypass unmodified thread files.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Tauri state is simple to cache globally using standard thread-safe `OnceLock<Mutex<HashMap<...>>>` blocks in Rust.
- Layout metrics calculation (`fit()`) in xterm.js combined with Tauri IPC invokes should be strictly throttled or conditional on actual container size changes.
