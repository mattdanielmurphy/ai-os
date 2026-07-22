## Goal
The user requested adding a pseudo-toolbar with macOS stoplight buttons (close, minimize, maximize) and window dragging support to the transformed Gemini webview, as well as making the window significantly larger upon transformation.

## User Feedback & Decisions
- Add macOS traffic lights (red, yellow, green) on a custom top pseudo-toolbar.
- Enable window dragging via the pseudo-toolbar.
- Expand transformed window size significantly (using `LogicalSize(1280, 880)` and screen centering instead of small physical sizes).

## Changes Made
- Modified `/Users/matt/projects/ai-os/tauri-gui/src-tauri/src/main.rs`:
  - Added `injectPseudoToolbar()` function inside `floating_init_script` to render a 38px fixed glassmorphic titlebar at top of document.
  - Added macOS stoplight buttons wired to Tauri window commands: `#aios-close-btn` -> `appWindow.hide()`, `#aios-min-btn` -> `appWindow.minimize()`, `#aios-max-btn` -> `appWindow.toggleMaximize()`.
  - Added draggable region behavior on mouse down over non-button toolbar areas calling `appWindow.startDragging()`.
  - Converted window sizing logic in both Rust (`floating_window.set_size`) and JS (`transformToNormalWebview()`) to `LogicalSize` (`1280x880` logical pixels) and invoked `appWindow.center()` upon transformation.
- Updated `FEATURES.md`.
- Updated `DEVELOPMENT_JOURNAL.md`.

## What Worked
- `cargo check` verified clean compilation.
- Pseudo-toolbar renders above webview content with smooth window dragging and native window action callbacks.

## What Didn't Work / Known Issues
- None.
