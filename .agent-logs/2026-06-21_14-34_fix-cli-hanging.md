## Goal
Diagnose and resolve a "hanging" state in the AI-OS CLI tool that occurred during the "Executing instruction via Direct API Fallback" phase. The CLI would freeze for 2 minutes instead of returning a response.

## Changes Made
- Modified the `callGemini` function in `src/index.js` to use a more robust JSON extraction mechanism instead of simply searching for `{` and `}` indexes.
- Added strict checks for `agy` outputs that start with `Error: ` on both `stdout` and `stderr`. If detected, the `callGemini` Promise resolves immediately with the error text and kills the stalled `agy` child process.

## What Worked
- Replacing the rudimentary JSON parsing logic with an `extractJson` function that checks for Markdown blocks (` ```json ... ``` `) and correctly matches the boundaries of JSON payloads within stream buffers.
- Catching `Error: timed out waiting for response` explicitly. The root cause of the 2-minute freeze was the `agy` node wrapper returning an error but never shutting down the event loop or closing the pipes. By detecting this on `stdout` and calling `child.kill()`, we avoid the 120-second fallback timeout.

## What Didn't Work / Known Issues
- `agy` CLI seems to hold the process open indefinitely if it encounters a rate limit or API timeout, rather than exiting with a non-zero code. This necessitates the aggressive early exit handling inside `callGemini` for both success parsing and error detections.

## Architecture Notes
- The `executeInstructionDirectly` relies on an iterative prompt loop where `useJson = true`. Any failure in the parsing logic for these PTY streams will cause silent hangs.
- When `useJson = false`, `callGemini` relies on `child.on('close')`. If `agy` does not exit automatically, these non-JSON queries might still be prone to hangs if they fail silently without emitting an explicit `Error: ` prefix.
