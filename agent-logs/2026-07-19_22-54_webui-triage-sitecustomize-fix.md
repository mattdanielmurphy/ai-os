## Goal
Fix the Hermes WebUI triage interceptor. The TUI (`hermes` command) correctly routes coding prompts through `agy` via `aios_hermes_wrapper.py`, but the WebUI (running at `http://127.0.0.1:8787`) did NOT receive the same triage interception — it would try to hit the `agy` provider directly (or use a fallback model) without routing through our custom patch.

## User Feedback & Decisions
- User confirmed the TUI and Zed both work correctly with the agy provider, verified by checking `/resume` in the TUI.
- User asked why it works in TUI but not WebUI — this was the key question answered this session.

## Changes Made

### Root Cause Identified
The WebUI is a **separate, long-lived Python server process** (launched via `ctl.sh`/`bootstrap.py`) that directly imports `run_agent.AIAgent` in-process. It **never runs** `aios_hermes_wrapper.py`, so the monkey-patch on `interruptible_api_call` was never applied.

### Fix: `webui-patches/sitecustomize.py`
- **Created**: `/Users/matt/projects/ai-os/webui-patches/sitecustomize.py`
  - Python auto-executes `sitecustomize.py` at interpreter startup when its directory is on `PYTHONPATH`.
  - Detects when the hermes-agent is on `sys.path` (i.e., we're in the WebUI process), then patches `agent.chat_completion_helpers.interruptible_api_call` and `interruptible_streaming_api_call` identically to the TUI wrapper.
  - Falls back to a lazy meta-path hook if hermes-agent isn't on sys.path yet at time of sitecustomize execution.

### Fix: `/Users/matt/projects/external/hermes-webui/.env`
- Added `PYTHONPATH=/Users/matt/projects/ai-os/webui-patches` so Python finds our `sitecustomize.py` at startup.
- `bootstrap.py` prepends `HERMES_WEBUI_AGENT_DIR` to `PYTHONPATH` at runtime; since `hermes-agent/sitecustomize.py` doesn't exist, Python falls through to our file.

## What Worked
- WebUI restarted and log confirmed: `[AIOS WebUI Triage] Patch installed on agent.chat_completion_helpers` ✅
- The patch is now applied identically to both TUI and WebUI paths.

## What Didn't Work / Known Issues
- The `.env` file change (for `PYTHONPATH`) is in the external repo at `/Users/matt/projects/external/hermes-webui/.env`. This file is gitignored or local-only — it won't be committed upstream. If hermes-webui is ever re-cloned, the `.env` will need to be re-created.
- `sitecustomize.py` approach requires a WebUI restart when changed.
- The lazy hook (`_register_lazy_hook`) was added as a fallback but may not be needed in practice since config.py adds the agent dir to sys.path before the first agent import.

## Architecture Notes
- **TUI**: runs `aios_hermes_wrapper.py` → patches `helpers.interruptible_api_call` → imports `hermes_cli.main`
- **WebUI**: runs `bootstrap.py` → starts a Python server → server imports `run_agent.AIAgent` directly via `agent_runtime.py:require_ai_agent_class()`
- The WebUI gateway mode (`HERMES_WEBUI_CHAT_BACKEND=gateway`) bridges to the Hermes API server on port 8642, but the default "legacy" mode runs the agent in-process in the WebUI server.
- `bootstrap.py` always prepends `HERMES_WEBUI_AGENT_DIR` to `PYTHONPATH`, so `sitecustomize.py` must not exist in the hermes-agent checkout (confirmed it doesn't).

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/ca657acc-ece2-4393-aa5c-0ed1d94fddf9/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/ca657acc-ece2-4393-aa5c-0ed1d94fddf9/.system_generated/logs/transcript.jsonl)
