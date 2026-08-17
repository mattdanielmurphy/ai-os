# Tauri Native IPC Callback Bridge for Companion Webviews

## Summary
Updated `apps/gemini-companion/src-tauri/src/server.rs` to use native Tauri IPC (`window.__TAURI__.invoke('query_callback', ...)` and `window.__TAURI_INVOKE__`) for returning query and debug ping results from webviews (Perplexity and Gemini) back to the Rust server.

## Changes
- Updated `sendDone()` in `handle_perplexity_query` and `handle_gemini_query` to invoke the `query_callback` Tauri command.
- Updated `handle_debug_ping` and `handle_debug_ping_gemini` to pass diagnosis strings back via Tauri IPC with graceful fetch fallback.
- Confirmed `cargo check` passes cleanly.
