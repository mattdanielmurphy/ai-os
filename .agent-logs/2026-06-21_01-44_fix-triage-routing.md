## Goal
Improve the AI-OS Gateway's triage routing logic to ensure that workspace troubleshooting requests, bug reports, and rendering issues are correctly routed to the execution tier with tool access (`TIER3_HEAVY`).

## Changes Made
- Modified `src/index.js` triage system instruction to explicitly mandate that user reports about programs, scripts, or layouts being broken or not working (even if they do not explicitly request a command or file read) must be routed to `TIER3_HEAVY`. This guarantees that the agent has terminal and filesystem access to diagnose the issue.
- Restored the corrupted test files in the `/Users/matthewmurphy/projects/tic-tac-toe` directory to their original states (including single-line formatting with escape characters in `style.css` and corrupt markup in `index.html`) so the user can accurately test the gateway tool.
- Documented "Workspace-Aware Triage Routing" in `FEATURES.md`.

## What Worked
- Successfully enhanced the gateway routing instructions in `src/index.js`.
- Restored the test fixture codebase without leaving modifications.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The gateway uses a Flash model for triage. Without explicit instructions to route codebase debugging/troubleshooting to the PTY session (`TIER3_HEAVY`), the triage model default-routes complaints about symptoms (e.g. "it's not working") to `TIER2_FLASH` (planning-only), which is unable to execute tools to inspect or fix the filesystem.
