---
title: "Update `/Users/matt/projects/ai-os/litellm/config.yaml` and `/Users/ma"
date: "2026-08-10"
conversation_id: "4b51b432-85c3-4841-a877-7773daab1f63"
source: "antigravity"
---

# Update `/Users/matt/projects/ai-os/litellm/config.yaml` and `/Users/ma

## User

Update `/Users/matt/projects/ai-os/litellm/config.yaml` and `/Users/matt/projects/ai-os/litellm_config.yaml` to route `deepseek-v4-flash` directly to official DeepSeek (`deepseek/deepseek-chat`) instead of `openrouter/deepseek/deepseek-v4-flash`.

Also update `deepseek-v4-pro` to `deepseek/deepseek-reasoner` (or `deepseek/deepseek-v4-pro` depending on official provider naming, but specifically route the provider to official deepseek so that prompt caching pricing applies).

Specifically for OpenRouter provider configuration in LiteLLM:
To route openrouter models to use official DeepSeek provider endpoint on OpenRouter, OpenRouter supports provider routing preferences. But directly calling deepseek API directly via `deepseek/deepseek-chat` with `api_key: os.environ/DEEPSEEK_API_KEY` or using `provider: { order: ["DeepSeek"] }` in LiteLLM params / OpenRouter headers ensures official DeepSeek provider endpoints are used.

Let's check `litellm/config.yaml`:
In `litellm/config.yaml` and `litellm_config.yaml`, update `deepseek-v4-flash` (and suffix variants) to specify provider routing order or model target for official DeepSeek:
1. `model: deepseek/deepseek-chat` (or `openrouter/deepseek/deepseek-chat` with provider ordering `provider: { order: ["DeepSeek"] }`). Using `deepseek/deepseek-chat` (native deepseek provider) or configuring `provider: { order: ["DeepSeek"] }` on OpenRouter ensures official DeepSeek is used for lowest cache pricing.
2. In `litellm/config.yaml`:
For `deepseek-v4-flash`, `deepseek-v4-flash-high`, `deepseek-v4-flash-medium`, `deepseek-v4-flash-low`, and `haiku`:
Update `provider` block from `sort: throughput` to:
```yaml
    provider:
      order:
        - DeepSeek
      allow_fallbacks: true
```
And change `model` under `litellm_params` if appropriate, or keep `openrouter/deepseek/deepseek-v4-flash` with `provider: { order: ["DeepSeek"] }` so OpenRouter targets the official DeepSeek host instead of throughput-sorted third-party providers (like DeepInfra / Lepton / Novita).

Also in `litellm_config.yaml`:
Add `extra_headers` or provider config:
```yaml
      extra_headers:
        HTTP-Referer: "https://ai-os.local"
        X-Title: "AI-OS"
```
Or for OpenRouter provider routing:
```yaml
      provider:
        order:
          - DeepSeek
```

Target files:
- `/Users/matt/projects/ai-os/litellm/config.yaml`
- `/Users/matt/projects/ai-os/litellm_config.yaml`

---

## Assistant

Successfully updated the LiteLLM configuration files to route `deepseek-v4-flash` and `deepseek-v4-pro` (to `deepseek-reasoner`) to the official DeepSeek provider endpoint on OpenRouter, including the required provider ordering and `extra_headers`.

---
