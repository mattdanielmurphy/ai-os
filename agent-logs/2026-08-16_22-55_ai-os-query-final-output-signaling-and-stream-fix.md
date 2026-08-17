# AI-OS Query Final Output Signaling & Perplexity Stream Parsing Fix

**Date:** 2026-08-16 22:55  
**Context:** User reported that AI-OS queries do not signal when the final output has arrived, leaving agents in the dark and requiring extra tool calls to inspect output files.

## Summary of Root Causes & Fixes

1. **Stdout & Task Notification in `query_aios.js`**:
   - Added live periodic progress heartbeat (every 4s) to `stderr` showing elapsed time and model status.
   - When the final response arrives, `query_aios.js` now prints a conspicuous visual and structured completion banner to `stdout` containing full metadata (provider, model, thread ID, elapsed seconds, chars, words, lines, output file path) followed by the complete final text and a definitive `[END OF AI-OS FINAL OUTPUT]` marker.
   - Automatically writes clean markdown output to target file (`--output` / `--plan`) while simultaneously outputting the formatted response in stdout.

2. **Perplexity Stream Parsing Premature Termination Bug in `perplexity-engine.js`**:
   - Fixed `_parseStream` which was prematurely exiting on intermediate search step statuses (`parsed.status === 'completed'`).
   - Ensured stream consumption continues until stream close (`chunk.done`), `data === '[DONE]'`, or `parsed.final === true` / `parsed.text_completed === true` with non-empty answer.

3. **IPC Bridge & Gateway Timeouts in `server.rs`, `main.rs`, and `tauri.conf.json`**:
   - Increased query timeout from 180s to 600s to support deep multi-turn thinking models without premature drops.
   - Fixed IPC parameter collisions with Tauri's internal error callback parameter in `query_callback`.
   - Added all application windows (`gemini_main`, `perplexity_main`, `floating`) to `tauri.conf.json` with full allowlist and dangerous remote domain IPC permissions.

4. **Preflight Cookie Reference Bug in `pplx_quota.py`**:
   - Fixed `cookie_header` reference error by properly calling `get_pplx_cookies()`.

