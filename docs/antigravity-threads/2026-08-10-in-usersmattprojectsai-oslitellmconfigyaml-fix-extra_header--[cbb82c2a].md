---
title: "In `/Users/matt/projects/ai-os/litellm/config.yaml`, fix `extra_header"
date: "2026-08-10"
conversation_id: "cbb82c2a-bf93-4176-a529-c8602f4e28c9"
source: "antigravity"
---

# In `/Users/matt/projects/ai-os/litellm/config.yaml`, fix `extra_header

## User

In `/Users/matt/projects/ai-os/litellm/config.yaml`, fix `extra_headers`. `extra_headers` must be placed inside `litellm_params:`, not inside `provider:`.

For each `deepseek-v4-flash` / `deepseek-v4-pro` entry in `/Users/matt/projects/ai-os/litellm/config.yaml`:
```yaml
    litellm_params:
      model: openrouter/deepseek/deepseek-v4-flash
      <<: *common_params
      extra_headers:
        HTTP-Referer: "https://ai-os.local"
        X-Title: "AI-OS"
    provider:
      order:
        - DeepSeek
      max_price:
        <<: *flash_prices
      allow_fallbacks: true
```

Target file: `/Users/matt/projects/ai-os/litellm/config.yaml`

---

## Assistant

The requested changes have been applied to `/Users/matt/projects/ai-os/litellm/config.yaml`. The `extra_headers` blocks have been moved from under `provider:` to `litellm_params:` for all `deepseek-v4-flash` and `deepseek-v4-pro` model entries, including their high/medium/low variants and the `haiku` alias.

---
