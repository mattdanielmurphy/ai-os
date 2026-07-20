## Goal
Fix the `Scope not defined` error for the floating window on `gemini.google.com` and replace the JS code injection for compressed mode with the user's provided code.

## Changes Made
- Modified `src-tauri/tauri.conf.json` to add `dangerousRemoteDomainIpcAccess` for `gemini.google.com` on the `floating` window, allowing it to execute IPC requests like `open_devtools`.
- Replaced the script in `src-tauri/src/main.rs` for `floating_init_script` with the exact snippet provided by the user. Wrapped it in a `setTimeout` polling check because the container (`.input-area-container`) usually takes time to mount on the remote app. Retained the `Cmd+Option+I` shortcut listener as requested.

## What Worked
- Replaced the JS payload exactly as requested and solved the IPC scope error.

## What Didn't Work / Known Issues
- N/A

## Architecture Notes
- Tauri v1 explicitly requires `dangerousRemoteDomainIpcAccess` if a webview loaded via a remote URL (like `https://gemini.google.com`) needs to execute Tauri IPC commands.
