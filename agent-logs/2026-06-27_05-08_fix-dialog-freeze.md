## Goal
Fix Tauri UI freeze when opening an existing project directory dialog.

## Changes Made
1. **`src-tauri/src/main.rs`**:
   - Modified `select_directory` command to be `async fn` and use `tauri::api::dialog::FileDialogBuilder`'s async callback signature with a synchronization channel (`std::sync::mpsc`) instead of the blocking variant `tauri::api::dialog::blocking::FileDialogBuilder`. This offloads the file selection dialog event loops from blocking the main thread or Tauri's command dispatch.

## What Worked
- Changed the command from synchronous `fn` blocking call to `async fn` using channel rx/tx, keeping the event loop of Tauri running while waiting for user input on macOS.
- Verified compilation is clean using `cargo check`.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Tauri command system executes synchronous commands on a thread pool, but if blocking API dialogs are called, they can block the main GUI thread event loop on macOS, leading to deadlocks/app freeze.
- Spawning the dialog via callback and blocking the async worker thread with a channel avoids freezing the main Cocoa UI event loop.
