## Goal
Implement a native browser context extraction Tauri command (`get_browser_context`) in `src-tauri/src/main.rs`. The command needs to execute JXA to target Chrome Canary, extract URL, title, and body text (clamped to 20k chars), handle Apple Events permission errors, and return a JSON string/struct to the frontend.

## Changes Made
- Modified `src-tauri/src/main.rs` to add the `get_browser_context` async Tauri command.
- Defined a `BrowserContext` struct for the return type.
- Registered the command in `tauri::generate_handler!`.
- Handled macOS Apple Events / JavaScript execution permission errors by returning descriptive Error payloads to prompt the user if they haven't allowed JavaScript in Chrome Canary yet.

## What Worked
- Successfully compiled `src-tauri` after adding the struct and command.
- Successfully verified the JXA logic using standalone script execution.
- Gracefully handles Apple Events exception by intercepting it and passing up an actionable error message.

## What Didn't Work / Known Issues
- N/A

## Architecture Notes
- The command uses `osascript -l JavaScript -e <SCRIPT>` rather than standard AppleScript since parsing JSON from JavaScript is significantly easier and natively supported by macOS's OSA runtime.
