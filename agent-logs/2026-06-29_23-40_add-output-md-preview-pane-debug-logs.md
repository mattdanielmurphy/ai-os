## Goal
Add debug info for the `output.md` preview pane failing to open/load, and record this as a potential ongoing issue/quirk.

## Changes Made
1. Modified `src/main.ts`: Added `console.error` logging inside the catch block of the interval that polls the active project's `.ai-os/output.md` file.
2. Updated `memory/agent-quirks-and-workarounds.md`: Added "Issue 2: output.md Not Opening in Preview Pane" to document this ongoing quirk, potential causes (e.g. Tauri scope constraints), and mitigation/debugging paths.
3. Built the frontend (`pnpm build`) to ensure assets are fully compiled.

## What Worked
- Re-compilation of the Tauri frontend was successful (`dist/assets/index-C-iSFq0R.js`).
- Adding error logs to the catch block will output diagnostic errors to the inspector console if the filesystem read or exists check fails.

## What Didn't Work / Known Issues
- The exact root cause (e.g., Tauri's configuration scopes, file permission boundaries, or path mismatching) is still to be determined by examining the generated logs in the Web Inspector.
