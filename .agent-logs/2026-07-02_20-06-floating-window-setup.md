## Goal
Create a Spotlight-like floating window for the dual-mode AI-OS system.

## Changes Made
1. `src-tauri/Cargo.toml`: Added `global-shortcut`, `window-hide`, and `window-show` to Tauri features.
2. `src-tauri/tauri.conf.json`: Added "floating" window with specific attributes (transparent, alwaysOnTop, visible: false, decorations: false, hiddenTitle: true) and added `globalShortcut: { all: true }` to the allowlist.
3. `src-tauri/src/main.rs`: 
   - Imported `tauri::GlobalShortcutManager`.
   - In `tauri::Builder::default().setup(...)`, registered `Cmd+Option+Space` global shortcut to toggle the "floating" window visibility and focus it.
   - Added `.on_window_event` handler for the "floating" window to automatically hide itself when losing focus (`WindowEvent::Focused(false)`).

## What Worked
All modifications successfully completed.

## What Didn't Work / Known Issues
None so far.

## Architecture Notes
The "floating" window logic provides a minimal background service structure tied directly into Tauri's window lifecycle and global shortcut capabilities.
