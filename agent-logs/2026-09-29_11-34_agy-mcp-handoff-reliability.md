# Agy MCP Handoff Reliability

- **Date:** 2026-09-29 11:34 MDT
- **Incident:** The referenced Chrome-extension Codex task's first agy call passed `timeout=180000`; the bridge interprets this value in seconds and rejected it above the 86,400-second limit. Its retry used 600 seconds but could not find either executable because the extension-launched process had a stripped `PATH` without `~/.local/bin`.
- **Reporting failure:** The bridge returned the actual `agy` PATH warning in `warnings` but a generic “agy missing, gemini missing” top-level error. The assistant repeated the generic summary as if both remote backends were unavailable.
- **Changes:** Added standard POSIX user-bin fallback discovery, included capability reasons in no-backend errors in synchronous and supervised paths, and documented seconds in MCP timeout schemas and validation errors.
- **Runtime evidence:** Before changes, `agy_doctor` and a short agy MCP smoke call succeeded in the current desktop runtime. The stripped-PATH failure was established from the referenced task's recorded MCP response and process environment. After the edit, no tests or new smoke call were run.
- **Commit:** `859f3c5a` (auto-committed by the project hook). That commit also included the pre-existing `Discussions.html` change reported by preflight.
