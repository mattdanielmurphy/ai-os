## Goal
Revert the MCP Server refactor from a previous session and restore `ai-os` back to its native TUI/CLI environment. Integrate the logic from `test-agy.js` into the core `callGemini` engine, enabling `ai-os` to route all queries through the local `agy` binary with model `gemini-3.1-pro-low`.

## Changes Made
- Executed a hard git reset to `dadea5d` to restore the complete TUI and CLI loop implementation, wiping the MCP server changes.
- Rewrote the `callGemini` function in `src/index.js` to spawn `node-pty` instances executing the `agy` CLI instead of directly hitting the Google GenAI API endpoint.
- Integrated the structured extraction buffer logic: when `useJson = true`, `callGemini` streams output locally, intercepts native JSON structures on the fly, and kills the `agy` worker instance to conserve token bounds.
- Set the static CLI flag `--model gemini-3.1-pro-low` on all backend agent requests.

## What Worked
The TUI system and CLI flags are functionally restored. The PTY proxy successfully runs native shell commands to `agy` and cleans up background tasks reliably when extracting structured JSON payloads.

## What Didn't Work / Known Issues
Because this proxies via `agy`, accurate real-time token tracking metadata relies on default 0 metrics if it's stripped from the raw text stream.

## Architecture Notes
The `ai-os` CLI natively bootstraps instances of itself, meaning local rate limits apply.
