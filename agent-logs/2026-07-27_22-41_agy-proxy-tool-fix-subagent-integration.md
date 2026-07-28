# Agent Log: agy-proxy Tool Support & subagent.py agy Integration

**Date:** 2026-07-27
**Model:** Hermes (deepseek/deepseek-v4-flash via OpenRouter MOA)

## Summary

Fixed the agy-proxy to support tool/function calling (previously silently dropped tools),
and added `--use-agy` flag to subagent.py for spawning agy subagents in tmux.

## What Changed

### 1. agy-proxy (`services/agy-proxy/proxy.py`)
- **Broken:** `ChatCompletionRequest` Pydantic model only had `model`, `messages`, `stream`
  — no `tools`/`tool_choice` fields. Any request with tool schemas silently dropped them.
  Request with tools → concatenated to plain text → piped to `agy --print` (text-only mode).
- **Fix:** Added full OpenAI chat completions schema (`tools`, `tool_choice`, `ToolFunction`,
  `FunctionDefinition`, `ToolCall`). When tools are present, proxy forwards the full request
  to the real LiteLLM proxy on port 8082 (which supports tool calling natively).
  When no tools, preserves existing `agy --print` path (paid Google OAuth quota).

### 2. LiteLLM proxy restarted
- Port 8082 LiteLLM had been killed during testing. Restarted with correct flags
  (removed non-existent `--log_level` flag from `run_litellm.sh`).

### 3. subagent.py (`scripts/subagent.py`)
- Added `--use-agy` flag to spawn agy instead of claude in the `subagents` tmux session
- Added brain directory monitoring (`~/.gemini/antigravity-cli/brain/`) — watches for
  CHECKPOINT entries in `transcript_full.jsonl` to detect completed turns
- Verified working: `subagent.py -p "say hi in one word" --use-agy -m gemini-3.6-flash-low`
  returns "Hi"

### 4. Hermes config
- `delegation.max_spawn_depth: 2` (enables depth-2 subagent orchestration)
- `delegation.model: gemini-3.6-flash-low` (cheap workers via agy proxy)

## Key Findings

1. **Custom agy-proxy on 8080** — NOT the real LiteLLM proxy (which is on 8082).
   The Hermes custom_providers config points `provider: agy` to `base_url: localhost:8080/v1`.
   This proxy was tool-unaware, breaking `delegate_task` subagents.

2. **delegate_task subagents weren't broken** — they literally couldn't see tools.
   The request went to 8080, tools got dropped, model responded with text only.

3. **subagent.py claude path unreliable** — `claude --bare` often hangs at interactive
   prompt (``/resume`) instead of completing autonomously.

## Running Services

| Service | Port | Auth | Tool support |
|---------|------|------|-------------|
| agy-proxy | 8080 | agy CLI OAuth | ✅ tools → LiteLLM, no-tools → agy |
| LiteLLM | 8082 | API keys | ✅ Full OpenAI tool format |

## Files Touched
- `services/agy-proxy/proxy.py` — major rewrite for tool support
- `litellm/run_litellm.sh` — removed invalid `--log_level` flag
- `scripts/subagent.py` — added `--use-agy` flag
- `agent-logs/2026-07-27_22-41_agy-proxy-tool-fix.md` — technical documentation

## Next Steps
- Test full fan-out pattern: plan with agy sonnet → execute with delegate_task workers
- Delegate_task needs `/reset` to pick up `max_spawn_depth: 2`