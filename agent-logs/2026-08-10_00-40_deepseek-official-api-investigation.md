# DeepSeek → Official API Migration (Investigation, no edits made)

Date: 2026-08-10
Status: INVESTIGATED ONLY — user said "just investigate for now, don't actually make any edits." No key provided yet. No config changed.

## Problem
Hermes, Zed, and the LiteLLM proxy all route DeepSeek through **OpenRouter**
(`openrouter/deepseek/*`) instead of DeepSeek's official API, incurring
OpenRouter's markup and missing DeepSeek's very low official cache pricing.
Matt wants the official DeepSeek endpoint even though it's slower, for the
cache-pricing win (unless unavailable / insanely slow).

## Root cause
**No `DEEPSEEK_API_KEY` is set anywhere** (checked env, `~/.hermes/.env`,
`~/.zshrc` — only `OPENROUTER_API_KEY` is present). The stack can't hit the
official endpoint without this key, so OpenRouter became the only path.

## Where each consumer routes today
| Consumer | File | Current routing |
|---|---|---|
| Hermes session | `~/.hermes/config.yaml` | `deepseek/deepseek-v4-flash` via provider **openrouter** |
| Hermes MoA Deepseek preset | `~/.hermes/config.yaml` (lines ~127-144) | `deepseek-v4-pro` + `deepseek-v4-flash` via provider **openrouter** |
| LiteLLM (LIVE) | `/Users/matt/litellm/config.yaml` (:8082) | `deepseek-v4-flash` / `deepseek-v4-pro` / `haiku` → `openrouter/deepseek/*` |
| LiteLLM repo copy | `/Users/matt/projects/ai-os/litellm/config.yaml` | `openrouter/deepseek/*` (+ -high/-med/-low suffix aliases) |
| LiteLLM root copy | `/Users/matt/projects/ai-os/litellm_config.yaml` | `openrouter/deepseek/*` |
| Zed | `~/.config/zed/settings.json` | agent models provider **openrouter**, model `~deepseek/deepseek-v4-flash-latest`; claude-acp uses `deepseek-v4-pro-high` |

Note: the LIVE LiteLLM config is `/Users/matt/litellm/config.yaml`, launched by
`run_litellm.sh` → `litellm --config config.yaml --port 8082`. It is a
DIFFERENT, simpler file than the repo copies (no suffix aliases, no shorthand
anchors). Any fix must edit the live file AND the repo copies to keep them in
sync.

## What a switch requires
1. Add `DEEPSEEK_API_KEY` (via key/env mechanism — Matt's secrets constraint:
   never expose raw secret value in context/transcripts; only check
   existence/has_value).
2. Official DeepSeek model names are **`deepseek-chat`** / **`deepseek-reasoner`**
   — the `deepseek-v4-flash` / `deepseek-v4-pro` aliases are OpenRouter-specific
   and would need remapping. Verify against `https://api.deepseek.com/models`
   once a key exists (V4 may or may not map cleanly).
3. Edit all four consumers + MoA preset: provider openrouter → deepseek (or
   custom base_url `https://api.deepseek.com/v1`).
4. Sweep fallback strings: several configs use `deepseek-v4-flash` as the
   fallback target for gemini/claude/muse — must switch those too or traffic
   still leaks via OpenRouter.
5. Restart services: `la restart agy-proxy` and restart litellm / hermes after
   config edits; Hermes change needs a new session (/reset) to pick it up.

## Decision held
User didn't answer the follow-up prompt (timed out). Default = respect the
original "investigate only, no edits." Awaiting: a DeepSeek API key from Matt,
or a "go ahead" to wire config changes with the key pending.
