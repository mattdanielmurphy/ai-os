## Goal
The user wanted to customize the floating Gemini window to:
1. Spawn a new window with a fresh thread upon opening via keyboard shortcut (after being closed).
2. Add an expand/collapse button for resizing the window.
3. Remove the standard macOS window toolbar and implement a drag handle on the text input area when the window is compressed.
4. Make the window fully transparent, leaving only the floating text input visible.

## Changes Made
- Modified `src-tauri/Cargo.toml` to add the `macos-private-api` feature to the Tauri dependency, which enables the `transparent()` property on `WindowBuilder` in macOS.
- Updated `tauri.conf.json` to allow the `window` API in the Tauri allowlist.
- Modified `src-tauri/src/main.rs`:
    - Updated `WindowBuilder` for the floating window to include `.decorations(false)` and `.transparent(true)`, and set the initial URL to `https://gemini.google.com/app` to start a fresh thread.
    - Updated the global keyboard shortcut (`Cmd+Option+Space`) to run `window.eval("window.location.href = 'https://gemini.google.com/app';")` before showing the window. This effectively forces a refresh/new thread upon reopening.
    - Added JavaScript in `floating_init_script` to set `document.documentElement` and `document.body` backgrounds to `transparent`.
    - Added a `mousedown` event listener to the input `target` element to act as a drag handle via `window.__TAURI__.window.appWindow.startDragging()`.
    - Added an absolute positioned expand/collapse toggle button `↕️` to alternate the physical height of the window between 180 (compressed) and 800 (expanded) using `window.__TAURI__.window.appWindow.setSize`.

## What Worked
- Tauri's `.transparent(true)` combined with `decorations(false)` successfully created an opaque-less floating window layout.
- The `cargo check` build succeeded without errors, proving the `macos-private-api` integration for `WindowBuilder` resolved compilation issues.

## What Didn't Work / Known Issues
- `__TAURI__.window.PhysicalSize` relies on the window API being available on the frontend. The `window: { all: true }` property was added to `tauri.conf.json` allowlist to ensure it passes IPC.
- `transparent` WindowBuilder feature natively required the `macos-private-api` feature inside the Tauri cargo dependency for it to be accessible, which initially failed compilation without it.

## Architecture Notes
- The Tauri `floating_init_script` runs on page load and evaluates JS within the external `gemini.google.com` URL. Modifying this script enables complete DOM manipulation and injection of custom controls inside the web view, making the UI seamlessly integrate with the transparent backend window.
