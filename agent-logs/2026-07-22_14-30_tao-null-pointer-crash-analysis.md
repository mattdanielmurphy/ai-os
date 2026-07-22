## Goal
Investigate and document the root cause of the `SIGABRT` crash in `tao::platform_impl::platform::app::send_event` (macOS null-pointer dereference during key window event dispatch) and ensure rich backtraces are captured on future crashes.

## User Feedback & Decisions
- Analyzed crash stack trace from macOS crash log: `send_event` dereferenced null `key_window` pointer when handling a key-up/command key release event without an active focused key window.

## Changes Made
- `tauri-gui/src-tauri/src/main.rs`: Added explicit `std::env::set_var("RUST_BACKTRACE", "1");` at process launch so Rust panics in native dependencies capture full symbolicated stack traces directly into `~/.ai-os/crash_logs/`.

## What Worked
- Verified clean build via `cargo check --manifest-path tauri-gui/src-tauri/Cargo.toml`.
- Auto-committed and pushed updates cleanly to remote `main`.

## Architecture Notes
- The crash occurs in upstream `tao` crate (`tao-0.16.11/src/platform_impl/macos/app.rs:54`). When `Cmd+Key` keyup events occur while no native window has focus (or while transitioning window focus/decorations in macOS), `[this keyWindow]` returns `nil`, and sending `sendEvent:` to `nil` in Rust's Objective-C wrapper triggers `null pointer dereference occurred`.
