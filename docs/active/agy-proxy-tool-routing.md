# agy-proxy: Tool-Aware Routing Architecture

**Status:** Active · **Port:** 8080 · **Backend:** FastAPI + `agy` CLI

## Overview

`proxy.py` is a lightweight reverse-proxy that provides an OpenAI-compatible `/v1/chat/completions` endpoint backed by either the `agy` CLI (paid Google OAuth quota) or the real LiteLLM proxy (full tool support). It inspects each incoming request for a `tools` field and routes accordingly:

| `tools` present | Route | Backend | Capabilities |
|---|---|---|---|
| No | → `agy --print` (subprocess) | Google Gemini via agy OAuth | Text-only, no tool schemas |
| Yes (length > 0) | → LiteLLM proxy (port 8082) | Any LiteLLM-supported model | Full tool/function calling |

This hybrid approach preserves paid Google quota for simple chat requests while enabling tool calls (function schemas, structured tool-choice) through LiteLLM when needed.

---

## Architecture

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

---

## Code Paths

### Path A: No Tools → agy CLI (`run_agy_stream` / `run_agy_sync`)

1. Messages are flattened into a plain-text prompt via `_build_agy_prompt()` (simple `ROLE: content` concatenation).
2. `agy --dangerously-skip-permissions --print [--model X] [prompt]` runs as a subprocess.
3. **Streaming:** Each stdout line from `agy` is wrapped in an SSE `data: {...}` chunk with `delta.content`.
4. **Sync:** Entire stdout is captured as `choices[0].message.content`.

### Path B: Tools Present → LiteLLM (`_proxy_to_litellm` / `_proxy_to_litellm_stream`)

1. The full `ChatCompletionRequest` model (`messages`, `tools`, `tool_choice`, `stream`, `max_tokens`, `temperature`) is serialized and forwarded to `http://127.0.0.1:8082/v1/chat/completions` via `urllib`.
2. **Non-streaming:** Synchronous POST (via `run_in_executor` to avoid blocking the ASGI loop), returns parsed JSON as the response.
3. **Streaming:** All SSE lines from LiteLLM are collected in a thread (buffered, ~100K tokens max), then yielded asynchronously. Chunks are re-stamped with the original `request_id` and `created` timestamp.

---

## Pydantic Schema (OpenAI-Compatible)

```
ChatCompletionRequest
├── model: str
├── messages: List[Message]
│   ├── role: str
│   ├── content?: str
│   ├── tool_calls?: List[ToolCall]
│   │   ├── id: str
│   │   ├── type: "function"
│   │   └── function: Dict[str, Any]
│   └── tool_call_id?: str
├── stream: bool = False
├── tools?: List[ToolFunction]
│   ├── type: "function"
│   └── function: FunctionDefinition
│       ├── name: str
│       ├── description?: str
│       └── parameters?: Dict[str, Any]
├── tool_choice?: Any
├── max_tokens?: int
└── temperature?: float
```

---

## Key Design Decisions

1. **Tools presence is the sole routing heuristic.** Simple and covers all current consumers (Hermes `delegate_task`, custom agents). No fallback ambiguity.

2. **agy uses `--dangerously-skip-permissions`.** Required in proxy mode since there's no interactive terminal to approve prompts. Safe when the proxy is the sole entry point.

3. **LiteLLM streaming buffers in memory.** All SSE lines from LiteLLM are collected in a thread (blocking `urllib` read loop) before being yielded to the async generator. This avoids callback complexity but means the entire response sits in RAM — acceptable for typical LLM responses (< 100K tokens).

4. **Error handling:**
   - LiteLLM HTTP errors → wrapped in `502` JSON response with `proxy_error` type.
   - LiteLLM connection refused → `RuntimeError` → `502`.
   - agy subprocess errors → inline in the SSE stream as a `delta.content` with `finish_reason: "error"`.

---

## Running Services

| Service | Port | Auth | Tool support |
|---|---|---|---|
| agy-proxy | 8080 | agy CLI OAuth | ✅ tools → LiteLLM, no-tools → agy |
| LiteLLM | 8082 | API keys | ✅ Full OpenAI tool format |

---

## Exposed Models

```
agy                          (default agy model)
gemini-3.6-flash-low         (cheap Google tier)
gemini-3.6-flash-medium
gemini-3.6-flash-high
gemini-3.1-pro-low           (1M context)
gemini-3.1-pro-high
claude-sonnet-4-6
claude-opus-4-6-thinking
gpt-oss-120b-medium
```

---

## Usage

```bash
# No tools → agy quota
curl -s http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "gemini-3.6-flash-low",
       "messages": [{"role": "user", "content": "Say hello"}]}'

# With tools → LiteLLM
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

---

## History

- **2026-07-27:** Added tool-aware routing. Before this, `proxy.py` dropped the `tools` field and sent every request through `agy --print` (text-only). Breakage was silent — `delegate_task` subagents couldn't see tool schemas but wouldn't error. [[agent-log]](../../agent-logs/2026-07-27_22-41_agy-proxy-tool-fix.md)

---

## Related

- `../../services/agy-proxy/proxy.py` — the implementation
- `../../litellm/run_litellm.sh` — LiteLLM service runner
- `../../scripts/subagent.py` — consumer that triggered the fix (added `--use-agy` flag)