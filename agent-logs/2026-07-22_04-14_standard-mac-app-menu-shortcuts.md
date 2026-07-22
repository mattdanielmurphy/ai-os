## Goal
Implement full standard macOS application menu bar options (App, File, Edit, View, Actions, Window, Help) and native keyboard shortcuts across all app windows in `tauri-gui`.

## User Feedback & Decisions
- User requested that all standard macOS keyboard shortcuts and menu items work naturally (e.g. Cmd+F, Window options, New Window, etc.), and any function the app supports should ideally have a menu bar option.

## Changes Made
- Modified `tauri-gui/src-tauri/src/main.rs`:
  - Built a comprehensive native `tauri::Menu` structure containing App, File, Edit, View, Actions, Window, and Help submenus with native macOS menu items and accelerators (`Cmd+N`, `Cmd+W`, `Cmd+Z`, `Cmd+Shift+Z`, `Cmd+X`, `Cmd+C`, `Cmd+V`, `Cmd+A`, `Cmd+F`, `Cmd+R`, `Cmd+Alt+I`, `Cmd+M`, `Cmd+1`, `Cmd+2`, `Cmd+Alt+Space`).
  - Added an `.on_menu_event` handler in Tauri Builder to handle custom menu triggers (`new_window`, `find`, `reload`, `toggle_devtools`, `focus_gemini`, `focus_coding`, `toggle_quick_prompt`, `help_docs`).
- Created task tracker file `.devtool/features/mac-app-menu-and-shortcuts.md` and set status to `review`.
- Updated `FEATURES.md` with the new capability.

## What Worked
- `cargo check` inside `tauri-gui/src-tauri` passed with 0 errors.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Tauri 1.8 native menus must be constructed at the `tauri::Builder` initialization phase using `.menu(menu)` to register operating system accelerators cleanly on macOS.
