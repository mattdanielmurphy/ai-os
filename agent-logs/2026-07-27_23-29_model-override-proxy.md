# Agent Log: Model-Override Proxy

## Goal
Implement the `{MODEL=...}` prompt-tag override system in the agy-proxy, allowing `delegate_task` to embed a per-call model override. Also prepare the config for switching `delegation.model` to `"subagent"` (the placeholder that triggers override behavior).

## User Feedback & Decisions
- Use `{MODEL=alias}` syntax in the prompt string to override the delegation model per-call
- Strip the tag from ALL messages (not just the first) to prevent leaking to the LLM
- Fall back to `"agy"` (no `--model` flag) when `"subagent"` placeholder is set but no `{MODEL=...}` tag is found

## Changes Made

### `services/agy-proxy/proxy.py`
- **Step 1 — Fixed `_resolve_model()`** (lines 83–100): Replaced broken stub with correct implementation:
  - Removed dead duplicate loop
  - Fixed docstring (was claiming `(str, List)` return when actually returning `str`)
  - Inner loop strips `{MODEL=...}` from ALL messages, not just the matched one
  - `.strip()` on alias handles whitespace padding
  - Logger uses `[model-override]` tag for grepability
- **Step 2 — Added `_resolve_model()` call to `run_agy_sync()`**: Line 177 now calls `_resolve_model()` before building the prompt (mirrors `run_agy_stream()` behavior)
- **Step 3 — Added `"subagent"` placeholder guard**: Both `run_agy_stream()` (line 114) and `run_agy_sync()` (line 178) check if `model_name == "subagent"` after resolution and fall back to `"agy"` (which omits `--model` from the agy CLI command)
- **Step 4 — Added `"subagent"` to `AVAILABLE_MODELS`** (line 25): So the proxy recognizes it as a valid model

### `~/.hermes/config.yaml`
- **Step 5 — Manual step required**: The `delegation.model` field is protected by Hermes' config security. User must run: `hermes config set delegation.model subagent`

## What Worked
- All 7 unit tests pass (tag extraction, multi-message stripping, whitespace handling, first-wins, no-tag fallback, None content, tool-call-only)

## What Didn't Work / Known Issues
- Cannot edit `~/.hermes/config.yaml` programmatically — Hermes blocks it. User needs to run `hermes config set delegation.model subagent` manually
- Also need to add `"subagent"` to the `custom_providers.agy.models` list in `~/.hermes/config.yaml` for Hermes to recognize it as a model alias (manual edit)

## Architecture Notes
- `_resolve_model()` mutates messages in-place (Pydantic v1 allows this). Each request gets its own `messages` list from Pydantic parsing, so this is thread-safe per-request
- The `"subagent"` → `"agy"` fallback is safe because the existing `cmd` block already handles `model_name == "agy"` by omitting the `--model` flag
- LiteLLM path (tool-bearing requests) is NOT modified — model override for LiteLLM is lower priority since tags in tool prompts are unlikely