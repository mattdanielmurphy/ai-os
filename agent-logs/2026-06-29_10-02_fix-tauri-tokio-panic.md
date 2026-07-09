## Goal
Fix a runtime panic in the Tauri app due to `tokio::spawn` being called outside of a Tokio runtime, and suppress unused field warnings for the `ProjectSession` struct.

## Changes Made
* `src-tauri/src/main.rs`: 
  * Replaced `tokio::spawn` with `tauri::async_runtime::spawn` in `spawn_axum_server` to ensure the asynchronous task runs within Tauri's provided Tokio runtime.
  * Added `#[allow(dead_code)]` to the `ProjectSession` struct to silence compiler warnings about unused fields (`mini_pid` and `project_path`).

## What Worked
* `tauri::async_runtime::spawn` successfully provided the necessary context to spawn the Axum server without panicking.
* The warnings for the unused `ProjectSession` fields were suppressed successfully, leaving a clean `cargo build` output.

## What Didn't Work / Known Issues
* N/A

## Architecture Notes
* Tauri apps manage their own async runtimes. Direct usage of `tokio::spawn` without `#[tokio::main]` will fail since the main thread isn't configured as a Tokio runtime by default. Utilizing `tauri::async_runtime::spawn` aligns with Tauri's setup.
