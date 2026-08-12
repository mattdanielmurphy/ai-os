# DeepSeek through OpenRouter — provider pinning & the reasoning_content quirk

How the DeepSeek models route through the LiteLLM proxy (:8082) and the debugging
pattern when a DeepSeek completion "returns nothing."

## Alias → latest, already wired

The LiteLLM config (`/Users/matt/projects/ai-os/litellm/config.yaml`, the LIVE
file the :8082 process runs) maps the `deepseek-v4-flash` alias to
`openrouter/~deepseek/deepseek-v4-flash-latest`. So:

- **`deepseek-v4-flash` alias already means "latest"** — there is no separate
  `deepseek-v4-flash-latest` alias to point at. Requesting the plain alias IS
  requesting latest through the proxy.
- OpenRouter lists `~deepseek/deepseek-v4-flash-latest` (the `~` prefix is the
  rolling-latest pointer). The versionless `deepseek/deepseek-v4-flash-latest`
  returns HTTP 400 — the `~` is required.
- To switch Hermes' default model to deepseek-latest:
  `hermes config set model.default deepseek-v4-flash` (provider stays
  `custom:agy`; the alias resolves to latest on the proxy).

## Provider pinning (DeepSeek official, not resellers)

DeepSeek traffic goes through OpenRouter, but OpenRouter can route the same model
via multiple upstreams (resellers). To pin the OFFICIAL DeepSeek provider, LiteLLM
uses an `extra_body` block INSIDE `litellm_params` (NOT at model level — LiteLLM
ignores model-level `provider:`/`extra_body:`):

```yaml
litellm_params:
  model: openrouter/~deepseek/deepseek-v4-flash-latest
  extra_body:
    provider:
      order: ["DeepSeek"]
      allow_fallbacks: true
```

`extra_body` must be 6-space indented under `litellm_params`.
Config-level injection confirmed working (not just request-level).
Verify a live call returns `provider: DeepSeek` in the response envelope.

## The `reasoning_content` quirk — "content: None" is NOT a failure

A DeepSeek completion through the proxy can return:

```
CONTENT: None
PROVIDER: DeepSeek
```

Do NOT interpret this as a silent failure or dead model. DeepSeek `~latest`
emits a `reasoning_content` channel FIRST; `message.content` stays `null` when
`max_tokens` is too small to fit past the (empty/consumed) reasoning field.
When `max_tokens` is large enough, content appears normally:

- Small window → `content: None`, `reasoning_content` populated, `finish_reason` may be `length`.
- Adequate window → `content: '1, 2, 3'`, `reasoning_content: None`, `finish_reason: stop`.

**Diagnosis:** if `finish_reason: stop` and you only need routing confirmation,
`provider` + `finish_reason` are a positive signal even when `content` is null.
To see actual answer text, raise `max_tokens` substantially (e.g. 50+) rather than
debugging the model. Check the full choice envelope (`keys(choice)`) for a
`reasoning_content` field before concluding anything failed.

## Path used this session

- Hermes session model: `~/.hermes/config.yaml` → `model.default: deepseek-v4-flash`,
  `provider: custom:agy` (agy-proxy :8080 → LiteLLM :8082).
- Vision model: `~/.hermes/config.yaml` → `auxiliary.vision.model:
  google/gemini-3.5-flash-lite` (Flash Lite is the current/latest Flash Lite;
  `google/gemini-3.6-flash` was the prior value; the older `-2.0-flash` is
  deprecated on OpenRouter).