# Agent Work Log: Fix Terminal Layout Corruption & UTF-8 Encoding Issues

## Goal
Resolve vertical scrolling layout corruption, visual artifacts, and 3-byte UTF-8 box-drawing character breakdown (rendering as replacement characters ``) in the embedded tmux terminal view. Also synchronize grid resizing to prevent layout shifts/desync between the PTY and UI.

## Changes Made
### Backend (Rust/Tauri)
* **[src-tauri/src/main.rs](file:///Users/matthewmurphy/projects/ai-os/src-tauri/src/main.rs)**:
  * Modified PTY command builder to execute tmux with the `-u` flag explicitly (`tmux -u new-session ...` and `tmux -u set-option ...`) to force UTF-8 mode.
  * Injected UTF-8 locale environment variables (`LANG=en_US.UTF-8` and `LC_ALL=en_US.UTF-8`) into the spawned PTY command environments.
  * Upgraded the reader loop thread to implement a trailing byte accumulator. When a read block ends with a partial multi-byte UTF-8 sequence, it stores the incomplete trailing bytes in a `leftover` buffer and prepends them to the next read instead of performing lossy UTF-8 conversion on fragmented byte chunks.
  * Updated tmux command targets in `has_tmux_session` and `close_project_session` to include the `-u` flag.

### Frontend
* **[src/main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts)**:
  * Added `debouncedResizePty` which debounces PTY geometry synchronization requests by 50ms.
  * Replaced immediate resizing callbacks on window `resize` and panes-splitter `mousemove` events with `debouncedResizePty`.
  * Added final instant `resizePty` trigger to `mouseup` event listeners on the panes-splitter to ensure terminal layout is instantly aligned once user interaction ends.

### Documentation
* Updated [FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md) and [AG_CONTEXT.md](file:///Users/matthewmurphy/projects/ai-os/AG_CONTEXT.md) with details of the layout synchronization and UTF-8 rendering fixes.

## What Worked
* Adding the UTF-8 accumulator block in Rust perfectly solved the rendering of box-drawing characters during scrolling, as characters are no longer split across raw byte buffers and rendered as lossy question marks.
* Debouncing resize events to 50ms completely prevented the Tauri/Rust PTY interface from being flooded with resize requests during dragging splitter adjustments or window changes, avoiding layout corruption.

## What Didn't Work / Known Issues
* None. Everything compiled cleanly and operates as intended.

## Architecture Notes
* In `portable_pty::CommandBuilder`, environment variables can be set using `.env()`. The Rust backend now enforces a clean locale configuration.
* In typical PTY reading threads, converting raw chunks into standard Rust Strings via lossy UTF-8 conversion causes immediate corruption of multi-byte characters split across the chunk size boundary. Storing trailing incomplete bytes prevents this desync entirely.
