---
name: agy-proxy-tool-routing
description: agy-proxy on port 8080 routes tools→LiteLLM and no-tools→agy CLI
metadata:
  type: reference
---

The agy-proxy (`services/agy-proxy/proxy.py`) provides an OpenAI-compatible `/v1/chat/completions` endpoint on port 8080 with tool-aware routing:

- **No tools present** → runs `agy --print` subprocess (uses Google OAuth quota, text-only)
- **Tools present** → forwards full request to real LiteLLM proxy on port 8082 (full tool/function calling)

Before 2026-07-27, the proxy silently dropped the `tools` field, breaking `delegate_task` subagents that rely on function schemas. The fix added OpenAPI-compatible Pydantic schemas (`ToolFunction`, `FunctionDefinition`, `ToolCall`, `tool_choice`) to `ChatCompletionRequest`.

**Why:** Hermes config points `provider: agy` to `base_url: localhost:8080/v1`. The custom proxy was tool-unaware, so agentic frameworks sending tool schemas got text-only responses. Routing by `tools` presence is a simple heuristic that preserves paid Google quota for plain chat while enabling tool calls through LiteLLM.

**How to apply:** When adding new downstream consumers that send tool schemas, verify they hit the LiteLLM path. The LiteLLM proxy on 8082 must be running for tool requests to work. See [[agy-proxy-tool-routing]].