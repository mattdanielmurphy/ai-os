---
name: hermes-provider-setup
description: "Configure Hermes providers: custom, vision, OpenRouter, LiteLLM. Architecture, routing, and provider pinning."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, provider, openrouter, litellm, custom-provider, vision, deepseek]
    related_skills: [hermes-agent, la-launch-agent-manager]
    category: software-development
---

# Hermes Provider Setup

Configuring Hermes's model providers — direct API, custom proxies, vision pipeline, and provider-level routing preferences.

## Architecture Overview

Hermes sessions can route through three paths:

| Path | Provider config | When to use |
|---|---|---|
| **Direct OpenRouter** | `provider: openrouter` | No proxy needed; OpenRouter handles routing. Best for vision models (`auxiliary.vision`). |
| **Custom provider (LiteLLM proxy)** | `provider: custom:<name>` | Need to pin specific OpenRouter providers, control routing preferences, or apply `extra_body` tweaks that Hermes doesn't natively support. Session default only — vision typically goes direct. |
| **Custom provider (agy-proxy)** | `provider: custom:agy` | Google OAuth quota path for Gemini models. For agy MCP tool use, NOT for OpenRouter models. |

Matt's setup:
- **Session model** routes through `custom:litellm` → `:8082` LiteLLM (supports provider pinning, model aliases, extra_body)
- **Vision provider** routes direct to OpenRouter (no proxy needed for `vision_analyze`)
- **Agy** is exclusively for Google OAuth quota — the name `custom:agy` must NOT be used for OpenRouter routes

## Setting Up a Custom Provider

Registered in `~/.hermes/config.yaml` under `custom_providers`:

```yaml
custom_providers:
  - name: agy
    base_url: http://127.0.0.1:8080/v1
    api_key: agy-bypass
  - name: litellm
    base_url: http://127.0.0.1:8082/v1
    api_key: agy-bypass
```

Then set as the active provider:

```bash
hermes config set model.provider "custom:litellm"
hermes config set model.default "deepseek-v4-flash"
```

Config changes take effect on `/reset` (new session) — never mid-conversation.

## Vision Provider Setup

Vision (`vision_analyze` tool) routes separately from the session model. It goes under `auxiliary.vision` in config:

```bash
hermes config set auxiliary.vision.provider openrouter
hermes config set auxiliary.vision.model google/gemini-3.5-flash-lite
```

Matt prefers **Gemini 3.5 Flash Lite** for vision via OpenRouter — it's cheap, fast, and the results are comparable to 3.6 Flash.

## OpenRouter Model ID Notes

- **Rolling latest aliases** use a `~` prefix: `~deepseek/deepseek-v4-flash-latest`. Without the `~`, the versionless ID returns HTTP 400 from OpenRouter.
- Hermes's `/model` command auto-corrects `deepseek/deepseek-v4-flash-latest` → `~deepseek/deepseek-v4-flash-latest` at call time.
- The `~latest` alias currently resolves to `deepseek/deepseek-v4-flash-0731`.

## LiteLLM Provider Pinning

The LiteLLM config (`litellm/config.yaml`) pins OpenRouter to DeepSeek official via `extra_body` inside `litellm_params`:

```yaml
litellm_params:
  model: openrouter/~deepseek/deepseek-v4-flash-latest
  extra_body:
    provider:
      order: ["DeepSeek"]
      allow_fallbacks: true
```

Model-level `provider:` key is IGNORED by LiteLLM — `extra_body` must be nested under `litellm_params`. This prevents routing to resellers (e.g. DigitalOcean) that are 6-90x more expensive per cache-read.

## Pitfalls

- **`hermes config set` with list values** can mangle the YAML into a quoted string. Verify the resulting format in `config.yaml` and fix manually with Python string replacement if needed.
- **Never use `custom:agy` for OpenRouter routes.** `agy` = Google OAuth quota. The name must reflect the actual backend (e.g. `custom:litellm` for the LiteLLM proxy).
- **Config changes are session-bound.** After any provider/config change, do `/reset` or restart Hermes. No mid-conversation picks them up.
- **`model.base_url` is for custom providers only.** For built-in providers (`openrouter`, etc.), Hermes knows the base URL. Setting it explicitly can conflict.
- **Vision and session model are independent.** Matt's vision goes direct to OpenRouter; session goes through LiteLLM. Don't conflate them.