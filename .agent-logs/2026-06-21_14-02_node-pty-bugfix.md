## Goal
Fix `ERR_MODULE_NOT_FOUND` (neo-blessed missing) and `posix_spawnp` crashing issues that appeared when testing the `ai-os` CLI after reverting to the native TUI environment.

## Changes Made
- Ran `pnpm install` after safely clearing the lockfile to restore `neo-blessed`.
- Replaced `node-pty` with native `child_process.spawn` within `src/index.js` (for `callGemini`) and `src/ptyWrapper.js` (for `WarmPtySession`). Node 26 currently exhibits a binary compatibility crash (`posix_spawnp`) with `node-pty`, rendering it non-functional.
- Handled stdin/stdout pipes directly using `stdio: ['pipe', 'pipe', 'pipe']`.

## What Worked
The codebase effectively proxies prompts directly via the native `child_process` `spawn` to the `agy` cli binary, correctly intercepting stdout and sidestepping the PTY binding bug. TUI interface restored without missing dependency errors.

## What Didn't Work / Known Issues
No major issues detected.

## Architecture Notes
We dropped `node-pty` system-wide. Native pipes handle structured text interception perfectly well without the overhead or platform sensitivity of pseudoterminal bindings.
