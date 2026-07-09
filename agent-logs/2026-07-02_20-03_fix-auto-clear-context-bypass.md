## Goal
Fix an issue where historical context was unnecessarily injected into the prompt when bypassing auto-clear to continue an existing agy thread.

## Changes Made
- Modified `src/main.ts` at line 2516 to include a check `!isBypass` before deciding to `/clear` and inject historical context.
- If `isBypass` is true (the user turned off auto-clear), the engine now skips `/clear` and sends the `processedInput` directly to the active thread, avoiding redundant context injection.
- Rebuilt the project using `pnpm build`.

## What Worked
- Modifying the conditional block successfully prevents the `/clear` and context injection when `isBypass` is true.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The `isBypass` variable correctly tracks when the user turns off the auto-clear setting for a prompt. This is vital for determining whether a command should be evaluated in a fresh context or the existing context.
