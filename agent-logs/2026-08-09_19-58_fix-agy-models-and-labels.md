# Agent Log: Fix agy Antigravity Models, Labels, and Resolution

**Date:** 2026-08-09 19:58  
**Author:** Antigravity  
**Files Modified:** `services/agy-proxy/proxy.py`, `tests/test_agy_proxy.py`, `~/.hermes/config.yaml`

## Problem
1. When selecting models under the `agy` provider in Hermes WebUI, 21+ models from LiteLLM (Claude 5, DeepSeek V4, Muse Spark, Grok 4.5) were erroneously exposed under `agy`. `agy` is Antigravity and should strictly offer Antigravity models.
2. `gemini-3.5-flash` / `gemini-3.5-flash-lite` was showing up under `agy` when it shouldn't.
3. Model labels were rendering with all-caps "LOW" (e.g. `Gemini 3.6 Flash LOW`) due to default title-casing heuristics when raw strings were passed without metadata.
4. Model effort flags (`-low`, `-medium`, `-high`) were passed as part of the model string rather than splitting `--model` and `--effort` flags for the `agy` CLI.

## Resolution
1. **Curated Antigravity Model Catalog in `proxy.py`**:
   - Replaced dynamic LiteLLM forwarding in `list_models()` with the exact 8 Antigravity models and explicit human-friendly names:
     - `gemini-3.6-flash-low` -> `Gemini 3.6 Flash (Low)`
     - `gemini-3.6-flash-medium` -> `Gemini 3.6 Flash (Medium)`
     - `gemini-3.6-flash-high` -> `Gemini 3.6 Flash (High)`
     - `gemini-3.1-pro-low` -> `Gemini 3.1 Pro (Low)`
     - `gemini-3.1-pro-high` -> `Gemini 3.1 Pro (High)`
     - `claude-sonnet-4.6` -> `Claude Sonnet 4.6 (Thinking)`
     - `claude-opus-4.6` -> `Claude Opus 4.6 (Thinking)`
     - `gpt-oss-120b` -> `GPT-OSS 120B (Medium)`
2. **Proper CLI Model & Effort Splitting in `_build_cmd_and_prompt()`**:
   - Normalized model names and extracted effort suffixes (`-low`, `-medium`, `-high`) to pass `--model <base>` and `--effort <level>` explicitly to `agy`.
   - Prevented placeholder names like `agy` and `subagent` from appearing as choices in the model picker.
3. **Config & Cache Synchronization in `~/.hermes/config.yaml`**:
   - Cleaned `model.aliases` and updated `custom_providers` so that `agy` models dynamically discover with accurate labels without duplicating stale entries.
   - Cleared stale webui model cache files.
4. **Verification**:
   - All 13 unit tests in `tests/test_agy_proxy.py` pass.
   - Verified `/v1/models` returns the exact 8 models with proper labels.
   - Verified Hermes WebUI `get_available_models()` renders the clean catalog without modifying any `hermes-webui` repository code.
