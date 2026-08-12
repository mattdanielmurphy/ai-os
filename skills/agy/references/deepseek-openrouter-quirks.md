# DeepSeek on OpenRouter — verification probes & transcripts

Captured 2026-08-11 while reconfiguring Hermes main-session model from
`custom:agy` proxy to direct `openrouter`. All probes run against the live
OpenRouter API with `OPENROUTER_API_KEY` from `~/.hermes/.env`.

## 1. List deepseek flash models on OpenRouter

```bash
export OPENROUTER_API_KEY=$(grep -E '^OPENROUTER_API_KEY=' ~/.hermes/.env | head -1 | cut -d= -f2- | tr -d '"')
curl -s --max-time 30 "https://openrouter.ai/api/v1/models" | python3 -c "
import sys,json
data=json.load(sys.stdin)
for m in data.get('data',[]):
    mid=m.get('id','')
    if 'deepseek' in mid.lower() and 'flash' in mid.lower():
        print(mid)
"
```

Output (as of 2026-08-11):
```
~deepseek/deepseek-v4-flash-latest
deepseek/deepseek-v4-flash-0731
deepseek/deepseek-v4-flash
```

`~deepseek/...-latest` IS present — the `~` prefix is the rolling-latest
marker and is REQUIRED. The versionless `deepseek/deepseek-v4-flash-latest`
(no `~`) returns HTTP 400.

## 2. Direct completion against the latest alias (no proxy)

```bash
curl -s --max-time 60 -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"~deepseek/deepseek-v4-flash-latest","messages":[{"role":"user","content":"Count from 1 to 3"}],"max_tokens":200}'
```

Result: `MODEL: deepseek/deepseek-v4-flash-0731`, `CONTENT: '1, 2, 3.'`,
`FINISH: stop`. The alias resolves to the newest snapshot.

## 3. The `content: None` quirk (not a failure)

With `max_tokens: 50`:
```
MODEL: deepseek/deepseek-v4-flash-0731
CONTENT: None
FINISH: length
```

With `max_tokens: 200`:
```
CONTENT: '1, 2, 3.'
FINISH: stop
```

DeepSeek v4 emits `reasoning_content` (reasoning channel) before `content`;
small `max_tokens` budgets get eaten by reasoning and `content` never
appears. `finish_reason: length` + `content: None` = budget too small,
NOT a routing failure. Bump max_tokens and retry. (Same quirk appears
through the LiteLLM proxy on :8082 — verify with `provider` field there:
`PROVIDER: DeepSeek` confirms official-provider pin.)

## 4. Provider-pin inside LiteLLM config (from earlier fix, verified)

```yaml
- model_name: deepseek-v4-flash
  litellm_params:
    model: openrouter/~deepseek/deepseek-v4-flash-latest
      extra_body:   # 6-space indent, INSIDE litellm_params — NOT model level
        provider:
          order: ["DeepSeek"]
          allow_fallbacks: true
```

- Model-level `provider:` / `extra_body:` keys are IGNORED by LiteLLM.
- `extra_body` nested under `litellm_params` is honored (verified: response
  `provider` field == `DeepSeek`).
- Stale copies of the config exist at `/Users/matt/litellm/config.yaml` —
  the LIVE one is `/Users/matt/projects/ai-os/litellm/config.yaml`
  (confirm via `lsof -p <pid> | grep cwd`).

## 5. Config shape that produced the wrong label (before/after)

Before (misleading):
```yaml
model:
  default: deepseek-v4-flash        # proxy alias
  provider: custom:agy              # routes to 8080 proxy!
  base_url: http://127.0.0.1:8080/v1  # stale once provider != custom:agy
```
UI label: `agy: deepseek-v4-flash` — wrong; deepseek rides OpenRouter.

After (honest):
```yaml
model:
  default: deepseek/deepseek-v4-flash-latest
  provider: openrouter
```
UI label: `openrouter: deepseek/deepseek-v4-flash-latest`.

Use `hermes config set model.provider openrouter`,
`hermes config set model.default deepseek/deepseek-v4-flash-latest`,
`hermes config unset model.base_url`. Config changes apply on a NEW
session (`/reset`) — never mid-conversation (prompt caching).
