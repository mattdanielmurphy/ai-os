## Goal
Fix the issue where simple exploratory requests (like "describe the files in this dir") were unnecessarily routed to the heavy `agy` CLI, and fix the issue where the `agy` CLI would stay open and never finish because it was running without a native PTY since `node-pty` was removed.

## Changes Made
- Modified `src/index.js` `triageSystemInstruction` to explicitly route simple, non-destructive exploratory requests (e.g. "describe the files in this dir") to `TIER1_LITE` with a "trivial" complexity.
- Modified `src/ptyWrapper.js` `WarmPtySession` to wrap the `bash` process in `script -q /dev/null`, which provides a true pseudo-terminal natively on macOS, preventing `agy` from hanging due to the absence of a PTY.

## What Worked
- Triage now correctly routes trivial read requests to the fast Direct API executor instead of spawning full agent loops.
- `script` wrapper successfully restores PTY context to background shells, allowing tools like `agy` to exit gracefully without hanging or requiring `node-pty`.

## What Didn't Work / Known Issues
None.

## Architecture Notes
The macOS native `script` utility serves as a reliable replacement for `node-pty` when `posix_spawnp` binary compatibility issues block it on newer Node versions (e.g. Node 26).
