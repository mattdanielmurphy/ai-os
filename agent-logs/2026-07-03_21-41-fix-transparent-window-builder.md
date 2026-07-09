## Goal
Fix compilation error in `src/main.rs`: `no method named 'transparent' found for struct 'WindowBuilder<'a, R>'`.

## Changes Made
1. **`src-tauri/Cargo.toml`**: Added `"macos-private-api"` to the `tauri` dependency features list. The `.transparent(true)` method on `WindowBuilder` in Tauri v1 relies on this feature flag when targeting macOS.
2. **`src-tauri/tauri.conf.json`**: Added `"macOSPrivateApi": true` to the `"tauri"` block. Tauri requires explicit acknowledgment in the config when using private macOS APIs.

## What Worked
Adding both the Cargo feature and the configuration flag resolved the compiler error. `cargo check` now passes successfully.

## What Didn't Work / Known Issues
Initially adding `"macOS": { "privateApi": true }` to the `bundle` block caused a `tauri-build` error because that was incorrect schema for Tauri v1. It needs to be `macOSPrivateApi: true` at the root of the `tauri` object.

## Architecture Notes
- The Tauri version used is 1.x.
- Transparent background support on macOS relies on private Apple APIs, which are gated by the `macos-private-api` Cargo feature and the `macOSPrivateApi` configuration setting. This prevents the application from being distributed through the Mac App Store.
