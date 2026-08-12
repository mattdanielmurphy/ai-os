---
name: agy-mcp-multi-tier
description: Route between cheap and expensive models via agy MCP tool.
version: 1.0.0
author: Matt + Hermes
created_by: agent
---

# agy MCP Multi-Tier Routing

Use the agy MCP tool (`mcp__agymcp__agy`) to route between cheap and
expensive models per-call. Unlike `delegate_task` (which uses a single
`delegation.model` for all subagents), agy MCP accepts a `model` parameter
for every invocation.

## Usage

```python
# Planning (expensive)
mcp__agymcp__agy(PROMPT="...", model="claude-sonnet-4-6")

# Execution (cheap)
mcp__agymcp__agy(PROMPT="...", model="gemini-3.6-flash-low")

# Review (expensive)
mcp__agymcp__agy(PROMPT="...", model="claude-sonnet-4-6")
```

## Available Models (agy proxy :8080)

- Cheap: `gemini-3.6-flash-low`, `gemini-3.6-flash-high`
- Mid: `gemini-3.1-pro-low`, `gemini-3.1-pro-high`
- Expensive: `claude-sonnet-4-6`
- Very expensive: `claude-opus-4-6-thinking`

## Why Not delegate_task

Confirmed 2026-07-27: `delegate_task` subagents get a ~100-word system
prompt and often complete with zero tool calls (just model identification
output). Root cause discovered: the **agy-proxy on port 8080 silently
drops `tools` and `tool_choice` parameters** from the OpenAI-format
request — its Pydantic models only had `model`, `messages`, and `stream`.
The subagent literally cannot see tool schemas.

**Fix applied 2026-07-27:** the proxy now forwards requests that contain
`tools` to the real LiteLLM proxy on port 8082, which handles tool
translation. Non-tool requests still use `agy --print` (preserves Matt's
paid Google OAuth quota). Tool-using requests go through LiteLLM →
OpenRouter API key billing.

Additional delegate_task constraints:
- **Config changes (model/provider/max_spawn_depth) need `/reset`** —
  the running session caches startup values. `hermes config set` writes
  the file but is ignored until next session.
- **`delegation.max_spawn_depth` must be >= 2** for orchestrator-role
  subagents to spawn their own workers. Default is 1 (flat).
- **No per-call model selection** — all subagents inherit
  `delegation.model`. Use agy MCP with `model` param for per-call control.

## Proxy Architecture (ai-os stack)

| Proxy | Port | Tool support | Billing |
|-------|------|-------------|---------|
| agy-proxy (custom FastAPI) | 8080 | ❌ native (forwards to LiteLLM when tools detected) | Google OAuth quota (no-tools path) |
| LiteLLM | 8082 | ✅ Full OpenAI tool format | OpenRouter API key |
| agy CLI | — | ❌ (text-only, agy --print) | Google OAuth quota |

The agy-proxy (`/Users/matt/projects/ai-os/services/agy-proxy/proxy.py`)
runs in the Hermes agent venv (`/Users/matt/projects/hermes-agent/venv/`).
LiteLLM runs via `/Users/matt/projects/ai-os/litellm/run_litellm.sh`.

## Fan-Out Plan Bridge Pattern

Combine agy MCP (expensive planner) + delegate_task (cheap workers):

```
User prompt → Main (cheap)
  ├─ Trivial? → respond directly
  ├─ Complex? → agy MCP(PROMPT="plan...", model="sonnet")
  │              Returns JSON plan
  ├─ Execute? → delegate_task(tasks=[plan steps])  # cheap workers
  └─ Review?  → agy MCP(...model="sonnet")          # expensive review
```

The planner sends a JSON array of tasks as its output. The main agent
reads the plan and fans out via `delegate_task(tasks=[...])`. This
avoids the `delegation.model` constraint — only the workers use
`delegation.model` (cheap), while the planner is selected per-call.

## Async Note

agy MCP dispatches async — the result arrives as a new chat message.
Structure workflows around dispatch → wait for result → continue.