## Goal
Configure Antigravity pre-flight check instructions to run quota CLI commands (`ag-quota -j` or `codexbar status`/`list`) and determine whether to automatically switch to minimal-token mode (Strict Orchestrator Mode 3) delegating heavy execution to `claude code` or cheap subagents via LiteLLM.

## User Feedback & Decisions
- User requested checking `ag-quota -j` or `codexbar` CLI tools at session start.
- Mode selection logic must auto-switch to minimal-token mode (Strict Orchestrator) when quota is low or burning rapidly.

## Changes Made
- **[AGENTS.md](file:///Users/matt/projects/ai-os/AGENTS.md)**: Updated Model Triage & Pre-Flight Quota Check section with step-by-step instructions to run `ag-quota -j` / `codexbar`, evaluate remaining fraction across models, and auto-switch to minimal-token mode.
- **[FEATURES.md](file:///Users/matt/projects/ai-os/docs/active/FEATURES.md)**: Added feature entry for Quota Pre-Flight Check & Minimal-Token Mode Auto-Switching.
- **[AG_CONTEXT.md](file:///Users/matt/projects/ai-os/AG_CONTEXT.md)**: Updated context summary bullet for quota routing & mode switching.
- **[DEVELOPMENT_JOURNAL.md](file:///Users/matt/projects/ai-os/DEVELOPMENT_JOURNAL.md)**: Added entry for 2026-07-22 summarizing the pre-flight quota rule and minimal-token mode pivot.

## What Worked
- Tested `ag-quota -j` and verified `codexbar` CLI tools.
- Updated all core configuration docs (`AGENTS.md`, `FEATURES.md`, `AG_CONTEXT.md`, `DEVELOPMENT_JOURNAL.md`).

## What Didn't Work / Known Issues
- `codexbar status` ran asynchronously due to shell wrapper behavior, but `ag-quota -j` returns instant JSON structure with exact model remaining fractions.

## Architecture Notes
- Antigravity callers run `ag-quota -j` pre-flight to measure quota and remaining fraction across models (e.g. Gemini 3.1 Pro/Flash, Claude Sonnet/Opus).

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/35798b3c-0e6d-4924-b487-47b97d4d257c/.system_generated/logs/transcript.jsonl)
