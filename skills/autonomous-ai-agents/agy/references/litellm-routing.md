# agy LiteLLM Routing Reference

Last verified: 2026-07-13. LiteLLM proxy at `localhost:8082`, config at
`/Users/matt/litellm/config.yaml`.

## Model Routing Table

| Model name | LiteLLM backend | Quota source | Cost |
|---|---|---|---|
| `gemini-2.5-flash` | `gemini/gemini-2.5-flash` | Google AI Studio (GEMINI_API_KEY) | API key quota |
| `gemini-2.5-pro` | `gemini/gemini-2.5-pro` | Google AI Studio (GEMINI_API_KEY) | API key quota |
| `gemini-2.5-flash-or` | `openrouter/google/gemini-2.5-flash` | OpenRouter | OpenRouter credits |
| `gemini-2.5-pro-or` | `openrouter/google/gemini-2.5-pro` | OpenRouter | OpenRouter credits |
| `deepseek-v4-pro-high` | `openrouter/deepseek/deepseek-v4-pro` | OpenRouter | OpenRouter credits |
| `deepseek-v4-flash-high` | `openrouter/deepseek/deepseek-v4-flash` | OpenRouter | OpenRouter credits |
| `deepseek-v4-flash-low` | `openrouter/deepseek/deepseek-v4-flash` | OpenRouter | OpenRouter credits |
| `deepseek-v4-flash-off` | `openrouter/deepseek/deepseek-v4-flash` | OpenRouter | OpenRouter credits |
| `hy3-free` | `openrouter/tencent/hy3:free` | OpenRouter free tier | **FREE** |
| `hy3-paid` | `openrouter/tencent/hy3` | OpenRouter (fallback) | Paid |
| `glm-5.2-agent` | `openrouter/thm/glm-5.2` | OpenRouter | Paid |
| `poolside-laguna-free` | `openrouter/poolside/laguna-m.1:free` | OpenRouter free tier | **FREE** |
| `nemotron-ultra-free` | `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter free tier | **FREE** |

## Critical: Gemini quota buckets are SEPARATE

The `gemini-2.5-flash` and `gemini-2.5-pro` models in LiteLLM route through
`gemini/gemini-2.5-*` — this hits Google's API directly using the
`GEMINI_API_KEY` environment variable. This is **NOT** the same quota as the
Antigravity consumer OAuth free tier that the `gemini` CLI uses
(`~/.gemini/oauth_creds.json`).

- **Google AI Studio API key** → `GEMINI_API_KEY` → LiteLLM `gemini/*` routes
- **Antigravity OAuth** → `~/.gemini/oauth_creds.json` → `gemini` CLI / agy `backend=gemini`

These are entirely separate quota pools. Do not assume free Antigravity quota
applies to LiteLLM Gemini models.

## Free models (truly zero-cost)

Three models route through OpenRouter's free tier:
- `hy3-free` — Tencent Hy3, 295B MoE, strong coding/reasoning
- `poolside-laguna-free` — Optimized for terminal execution and multi-file SE
- `nemotron-ultra-free` — NVIDIA, hybrid Transformer-Mamba, 1M context window

## Using LiteLLM as a Hermes provider

Hermes can point at this proxy as a `custom` provider:

```yaml
# ~/.hermes/config.yaml
model:
  default: "hy3-free"          # or any model from the table above
  provider: "custom"
  base_url: "http://localhost:8082/v1"
  # No api_key needed — Hermes trusts loopback URLs for custom providers
```

Hermes builds its full system prompt (memory, skills, SOUL.md, tool schemas)
and sends API calls to the LiteLLM proxy. Tool calling works because LiteLLM
translates between OpenAI tool format and the backend model's native format.

This preserves the full Hermes experience (system prompt, memory, skills, tool
loop) while changing only where the API call lands.

### Health check

```bash
# Verify LiteLLM is running
curl -s http://localhost:8082/v1/models | python3 -c "import sys,json; [print(m['id']) for m in json.load(sys.stdin)['data']]"

# Verify Hermes can reach it
hermes doctor
```

### Fallback routing

The LiteLLM config has simple-shuffle routing with these fallbacks:
- `gemini-2.5-pro*` → `gemini-2.5-pro-or` (OpenRouter fallback)
- `gemini-2.5-flash*` → `gemini-2.5-flash-or` (OpenRouter fallback)
- `hy3-free` → `hy3-paid` (paid fallback when free tier expires)

## agy MCP tool vs Hermes custom provider

| Approach | System prompt? | Tools? | Quota |
|---|---|---|---|
| `mcp__agymcp__agy(backend=gemini)` | ❌ Raw prompt | ❌ One-shot | ✅ Antigravity free |
| `mcp__agymcp__agy(backend=agy)` | ❌ Raw prompt | ❌ One-shot | agy's routing |
| Hermes `custom` → LiteLLM `hy3-free` | ✅ Full | ✅ Full loop | ✅ Free |
| Hermes `custom` → LiteLLM `gemini-2.5-flash` | ✅ Full | ✅ Full loop | ❌ API key quota |
