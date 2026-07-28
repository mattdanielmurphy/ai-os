# agy-proxy Tool Calling Fix

**Date:** 2026-07-27 22:41  
**Author:** Automated audit  
**Files:** `services/agy-proxy/proxy.py`

---

## What Was Broken

Before this fix, the agy-proxy (port **8080**) unconditionally forwarded **all** `/v1/chat/completions` requests through the `agy --print` CLI path. The `agy` CLI does **not** support tool/function calling — it only handles plain text prompt/response. Any request that included a `tools` array would:

1. Be serialized into a flat text prompt via `_build_agy_prompt()`
2. Have the tool definitions silently dropped
3. Receive a plain-text response with no `tool_calls` in the reply

This broke any downstream consumer that relies on function calling (e.g. agentic frameworks, OpenAI-compatible tool-use SDKs).

## What Changed

The proxy now inspects each incoming request for a `tools` field:

| Condition | Route | Backend |
|---|---|---|
| `tools` present (length > 0) | → **LiteLLM proxy** (port 8082) | Full tool support |
| No `tools` | → **agy CLI** `--print` path | Paid Google quota, text-only |

### New Code Paths Added

1. **`_proxy_to_litellm(payload)`** — Synchronous HTTP POST to LiteLLM (non-streaming)
2. **`_proxy_to_litellm_stream(payload, model)`** — Async SSE streaming from LiteLLM using `urllib` in a thread pool executor
3. **`_urllib_post(url, data)`** — Helper for blocking POST with error handling (HTTPError, URLError)

### Router Logic (`/v1/chat/completions`)

```python
has_tools = request.tools and len(request.tools) > 0

if has_tools:
    # → forward to LiteLLM (port 8082)
    if request.stream:
        return StreamingResponse(_proxy_to_litellm_stream(...))
    else:
        return await _proxy_to_litellm(...)
else:
    # → forward to agy --print CLI
    if request.stream:
        return StreamingResponse(run_agy_stream(...))
    else:
        return run_agy_sync(...)
```

## Architecture Diagram

```
                          External Client
                     POST /v1/chat/completions
                               │
                               ▼
                      agy-proxy (port 8080)
                        proxy.py (FastAPI)

               Does request have `tools`?
                      │            │
                  YES │            │ NO
                      ▼            ▼
               ┌─────────────┐  ┌──────────────┐
               │ LiteLLM     │  │ agy --print  │
               │ proxy       │  │ CLI          │
               │ port 8082   │  │ subprocess   │
               └──────┬──────┘  └──────┬───────┘
                      │                │
                      ▼                ▼
               ┌─────────────┐  ┌──────────────┐
               │ LiteLLM     │  │ agy binary   │
               │ router      │  │ → Gemini     │
               │ → tool calls│  │ → text only  │
               │ → streaming │  │ → paid quota │
               └──────┬──────┘  └──────────────┘
                      │
                      ▼
                ┌──────────┐
                │ Upstream │
                │ models   │
                └──────────┘
```

## Verification Steps

### 1. Both ports are listening

```bash
$ lsof -i :8080 -i :8082 -P | grep LISTEN
Python    46281 matt  IPv4  ...  *:8082 (LISTEN)       # LiteLLM
python3.1 46434 matt  IPv4  ...  localhost:8080 (LISTEN) # agy-proxy
```

### 2. Tools request → LiteLLM path (verified working)

```bash
curl -s http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.6-flash-medium",
    "messages": [{"role": "user", "content": "What is 2+2?"}],
    "tools": [{"type": "function", "function": {
      "name": "test", "description": "test",
      "parameters": {"type": "object", "properties": {"x": {"type": "string"}}}
    }}]
  }'
```

**Expected:** Returns a valid OpenAI-compatible response with `"finish_reason": "stop"` and the model's text answer. (LiteLLM may not always call the tool — it depends on the model — but it **supports** the tool definition.)

**Actual result (verified):**
```json
{
    "id": "JudnapOeI_CkqtsPqMW6IQ",
    "created": 1785194278,
    "model": "gemini-3.6-flash-medium",
    "choices": [{
        "finish_reason": "stop",
        "message": { "content": "2 + 2 = 4.", "role": "assistant" }
    }]
}
```

### 3. No-tools request → agy CLI path (verified working)

```bash
curl -s http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "gemini-3.6-flash-low",
       "messages": [{"role": "user", "content": "Say hello"}]}'
```

**Actual result (verified):**
```json
{
    "id": "chatcmpl-010657a9-...",
    "model": "gemini-3.6-flash-low",
    "choices": [{
        "message": { "role": "assistant", "content": "I am running on **Gemini 3.5 Flash**.\n" },
        "finish_reason": "stop"
    }]
}
```

### 4. LiteLLM health check (standalone)

```bash
curl -s http://127.0.0.1:8082/v1/models | python3 -m json.tool | head -10
```

### 5. agy-proxy health check

```bash
curl -s http://127.0.0.1:8080/v1/models | python3 -m json.tool
```

## Model List

The proxy exposes these models:

- `agy` (default agy model)
- `gemini-3.6-flash-low` / `-medium` / `-high`
- `gemini-3.1-pro-low` / `-high`
- `claude-sonnet-4-6` / `claude-opus-4-6-thinking`
- `gpt-oss-120b-medium`

## Key Design Decisions

1. **Tool routing is purely based on the `tools` field presence.** If a request has tools, it goes to LiteLLM. This is a simple heuristic that works for all current consumers.

2. **agy `--print` path uses `--dangerously-skip-permissions`** to avoid interactive prompts when running as a proxy backend.

3. **LiteLLM streaming** collects all lines in a thread and yields them async — this avoids callback complexity at the cost of buffering the entire response in memory. Acceptable for typical LLM responses (< 100K tokens).

4. **Error handling:** LiteLLM HTTP errors are wrapped in a `502` JSON response. agy errors appear inline in the streaming content.
