# Agent Work Log: Switch Default Telegram Assistant AI Engine to Codex

- **Date:** 2026-09-19 14:41
- **Author:** Antigravity (Orchestrator)
- **Scope:** `services/assistant/`

## Context & Problem
During testing of `agy` (`gemini-3.8-flash-low`) as the default assistant query engine, the `agy -p` CLI invocation overhead introduced ~8-10 seconds of latency due to full agent environment initialization (worktrees, workspace scanning, preflight probes). The user requested an immediate return to OpenAI Codex (`openai-codex` via `hermes chat`) which responds in ~1-2s and directly utilizes their ChatGPT Codex subscription.

## Changes Made
1. **`services/assistant/config.py`**:
   - Changed `default_engine` default fallback from `"agy"` to `"codex"`.
2. **`services/assistant/tests/test_assistant.py`**:
   - Added assertion to verify that `AssistantConfig.default_engine == "codex"` by default.
   - Verified that the full pytest suite (15 tests) passes cleanly in <1s.
3. **LaunchAgent Service (`aios-assistant`)**:
   - Restarted `aios-assistant` via `la restart aios-assistant`.
   - Verified active boot and healthy logs in `tmux:agent-aios-assistant`.

## Verification
- Executed `/Users/matt/projects/ai-os/services/assistant/.venv/bin/pytest services/assistant/tests/`:
  - 15 passed in 0.60s.
- `la logs aios-assistant -n 30` confirms the daemon started with healthy calendar permissions and zero errors.
