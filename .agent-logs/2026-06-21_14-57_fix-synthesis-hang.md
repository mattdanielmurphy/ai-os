## Goal
Fix the execution hang occurring at the `Synthesizing execution response...` step. The user observed that despite the previous `script` fix for the warm PTY shell, direct non-JSON text synthesis was failing to resolve and timing out.

## Changes Made
- Modified `callGemini` in `src/index.js` to explicitly watch the `outputBuffer` for a unique text stream closure marker (`[END_OF_RESPONSE]`).
- Appended a `CRITICAL COMPLETION MARKER` directive to the internal system prompt for the `Synthesizing execution response` step, instructing the agent to always conclude its summary with `[END_OF_RESPONSE]`.
- Replaced the brittle `child.on('close')` event listener (which was hanging due to lingering unclosed standard pipes across nested internal processes) with a combination of `child.on('exit')` and explicit `child.kill()` teardown triggers.

## What Worked
The system now safely aborts the background process the precise millisecond the model finishes writing its string payload, entirely severing the tie to dangling shell descriptors.

## What Didn't Work / Known Issues
Attempts to rely purely on standard stream closures (`close`/`exit` events) with `agy` in standard headless piping modes (`--print -`) consistently result in indefinite blocking if a real PTY is not attached, making programmatic token intercepts mandatory.

## Architecture Notes
Because the `agy` CLI binary is structurally designed around an interactive TTY assumption (even when executing headless single-shot queries), the `node:child_process` orchestrator must aggressively manage cleanup. Rather than waiting on graceful exit codes or native pipe `EOF` signals that never propagate cleanly through the layers of the binary, pattern-matching the raw text stream for explicit completion flags provides completely deterministic orchestration.
