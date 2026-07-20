## Goal
Implement a reverse proxy (`scripts/triage_proxy.py`) for Hermes Agent to intercept and natively triage `prompt.submit` WebSocket events, avoiding expensive token context windows for simple boilerplate requests. Furthermore, ensure `AGENTS.md` is hidden during `agy` subagent spawns to avoid duplicate system prompts when invoked via `hermes serve`. Adjust the architecture for the `hermes-webui` ecosystem.

## User Feedback & Decisions
- The user clarified that the Tauri GUI backend (`tauri-gui/src-tauri`) is legacy and abandoned, and they are now using `~/projects/external/hermes-webui`.
- Decided to create a simple wrapper script (`scripts/start-triage-proxy.sh`) rather than modifying backend Rust code or WebUI code.

## Changes Made
- Reverted the obsolete changes applied to `tauri-gui/src-tauri/src/main.rs`.
- Created `scripts/start-triage-proxy.sh` to transparently spin up `hermes serve --port 9120` and `triage_proxy.py --port 9119 --target 9120`. 
- Updated `scripts/triage_router.py` with a `hide_agents_md()` context manager to rename `AGENTS.md` before `subprocess.call` invokes `agy`, restoring it afterwards.

## What Worked
- The `triage_proxy.py` script effectively runs as a middleman.
- Context manager cleanly hides/restores the project rule files.
- The wrapper script correctly boots both services into the background, providing a drop-in replacement that works cleanly with `hermes-webui` configuration defaults.

## What Didn't Work / Known Issues
- `uv pip install websockets` in the wrapper script may encounter an `externally-managed-environment` error on some macOS installations. It is guarded with `|| true` to gracefully continue since `websockets` may already be globally available.

## Architecture Notes
- `hermes-webui` defaults to port `8787` for its own service and `9119` for the `hermes serve` agent communication via WebSocket JSON-RPC 2.0.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-ide/brain/34a33f30-4176-4ddb-bc83-0b4aede61d63/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/34a33f30-4176-4ddb-bc83-0b4aede61d63/.system_generated/logs/transcript.jsonl)
