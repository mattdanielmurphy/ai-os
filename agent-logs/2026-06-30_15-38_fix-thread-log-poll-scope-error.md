## Goal
Fix the Tauri filesystem scope error thrown during the active thread log polling when checking if the log file exists.

## Changes Made
- Modified [src-tauri/src/main.rs](file:///Users/matthewmurphy/projects/ai-os/src-tauri/src/main.rs):
  - Created a new backend `file_exists` Tauri command to check if a path exists from Rust.
  - Registered the `file_exists` command in the Tauri invoke handler.
- Modified [src/main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts):
  - Substituted the frontend-restricted `exists(filepath)` function call (from `@tauri-apps/api/fs`) with the backend-based `invoke('file_exists', { filepath })` call inside the active thread log polling `setInterval`.
  - Removed the now unused import of `{ readTextFile, exists }` from `@tauri-apps/api/fs` to prevent TypeScript compilation failures.

## What Worked
- Implementing and registering the `file_exists` Rust backend Tauri command.
- Replacing the frontend scope-restricted `exists` check with the backend invoke call.
- Verifying the project build status by running frontend build and Rust compile checks.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Tauri filesystem scope security limits apply to frontend-initiated `fs` module operations (like `exists`, `readTextFile`) when accessing directory paths outside of Tauri's configured allowlist scope (such as hidden directory configurations like `.gemini/` or `.agent-logs/`). Using a backend Tauri command bypasses this sandbox.
