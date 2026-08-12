# Session Reference: Vision + Provider Routing Setup

Date: 2026-08-11
Models used: deepseek/deepseek-v4-flash-latest (session), google/gemini-3.5-flash-lite (vision)
Provider: openrouter (vision), custom:litellm → :8082 (session)

## What was accomplished

1. **Vision pipeline** — attached Gemini Flash Lite via OpenRouter as the auxiliary vision provider
2. **Provider routing decoupled** — separated agy (Google OAuth) from LiteLLM (OpenRouter with provider pinning)
3. **Default model pinned** — session model routes through LiteLLM on :8082, which pins DeepSeek official

## Before → After: config.yaml model block

| Key | Before | After |
|---|---|---|
| `model.provider` | `custom:agy` | `custom:litellm` |
| `model.default` | `gemini-3.6-flash-low` | `deepseek-v4-flash` |
| `model.base_url` | `http://127.0.0.1:8080/v1` | *(removed)* |
| `custom_providers` | `[{name: agy}]` | `[{name: agy}, {name: litellm}]` |
| `auxiliary.vision.provider` | *(not set)* | `openrouter` |
| `auxiliary.vision.model` | *(not set)* | `google/gemini-3.5-flash-lite` |

## Verification commands

```bash
# Test direct OpenRouter vision model
OPENROUTER_KEY=$(grep -E '^OPENROUTER_API_KEY=' ~/.hermes/.env | head -1 | cut -d= -f2- | tr -d '"')
curl -s -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"google/gemini-3.5-flash-lite","messages":[{"role":"user","content":[{"type":"text","text":"Describe this screenshot."},{"type":"image_url","image_url":{"url":"data:image/png;base64,..."}}]}]}'

# Test session model through LiteLLM
curl -s -X POST http://127.0.0.1:8082/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"Reply OK"}],"max_tokens":20}'
# Expected: PROVIDER: DeepSeek, content returns text

# List models from LiteLLM
curl -s http://127.0.0.1:8082/v1/models
```

## Key insight

The agy proxy on :8080 routes to agy CLI (Google OAuth). The LiteLLM proxy on :8082 routes to OpenRouter with DeepSeek pinning. They are entirely separate backends. The `custom:agy` label should NEVER be used for OpenRouter-routed models, only for actual agy-backed Gemini calls.