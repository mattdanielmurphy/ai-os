# Dedicated Query AIOS Companion

**Date:** 2026-09-22
**Objective:** Replace the development-only AI-OS GUI runtime with the smallest persistent runtime needed by `query_aios`.

## Changes

- Added `apps/query-aios-companion/src-tauri`, a production-only Tauri companion that exposes the existing local query bridge without Vite, the workspace frontend, PTYs, terminal sessions, menus, or global shortcuts.
- The process opens one hidden Perplexity webview at startup. Gemini is hidden and created only for an explicit Gemini query.
- Configured macOS accessory activation, App Nap suppression, close-to-hide behavior, and exit-request prevention so normal user actions do not discard the warmed browser context.
- Added the package to the root Cargo workspace and switched `scripts/run_aios_server.sh` to execute `target/release/query-aios-companion` directly. The launcher no longer touches Vite's port 1420.

## Verification

- `cargo check -p query-aios-companion` and `cargo build --release -p query-aios-companion` passed.
- The active service reports one hidden Perplexity webview and no Gemini webview.
- A warm default query returned `AIOS_HIDDEN_OK` in 1.70 seconds.
- A forced complete service recovery returned `AIOS_LEAN_RECOVERY_OK` in 13.64 seconds. The remaining cold-start time is first-page webview loading; it no longer includes Vite or Rust compilation.
