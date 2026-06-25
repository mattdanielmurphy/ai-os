## Goal
Fix the issue where tasks falling back to `TIER1_LITE` or routed to `TIER2_FLASH` stopped prematurely because the Gemini Direct API path only returned raw command text instead of executing it.

## Changes Made
- Modified `src/index.js` to route `TIER1_LITE` and `TIER2_FLASH` (the `else` block / Gemini Direct API path) through `executeInstructionDirectly`.
- Integrated response synthesis in the direct API execution path to match `TIER3_HEAVY` output formatting.
- Updated `FEATURES.md` to document the new `Direct API Execution Fallback` capability.

## What Worked
- Replaced the simple, text-only `callGemini` invocation in `src/index.js` with the full `executeInstructionDirectly` loop and response synthesis, ensuring filesystem changes and command executions are actually run.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The gateway's Direct API path previously assumed that the user only wanted text-only execution node context output, ignoring the actual execution actions. With this fix, both local PTY-based and Direct API paths are fully action-capable.
