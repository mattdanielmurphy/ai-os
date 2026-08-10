# Handoff — DeepSeek → official provider pin + v4-flash-latest (LIVE config edited, proxy NOT yet restarted)

Date: 2026-08-10
Status: **CONFIG EDITED AND CORRECT ON DISK. PROXY NOT YET RESTARTED. VERIFICATION PENDING.**
Resume from here in a fresh thread. Do NOT re-investigate from scratch — the root cause is proven and the fix is applied.

---

## The bug (proven, don't re-derive)
DeepSeek traffic WAS going through OpenRouter (as desired). But the "prefer DeepSeek official" pin was silently broken:
- The running LiteLLM uses `/Users/matt/projects/ai-os/litellm/config.yaml` (confirmed via process cwd of the `:8082` litellm). `/Users/matt/litellm/config.yaml` is a STALE COPY — ignore it.
- The old config had `provider: {order: [DeepSeek], max_price, allow_fallbacks}` as a **model-level** key. LiteLLM IGNORES that key. Verified through the running proxy: a `deepseek-v4-flash` call returned `provider: DigitalOcean`, not DeepSeek.
- That's the cost leak: DeepSeek official cache-read = **$0.0028/M (flash)** / **$0.0036/M (pro)**. DigitalOcean = $0.0168/M; others up to $0.33/M (~90x worse).

## The fix mechanism (VERIFIED working — 3 ways: direct OpenRouter, via litellm.completion, via throwaway proxy on :8099)
- Correct model id for the rolling latest alias = **`openrouter/~deepseek/deepseek-v4-flash-latest`** (the `~` is required; versionless `deepseek/deepseek-v4-flash-latest` returns 400).
- **`extra_body: {provider: {order: ["DeepSeek"], allow_fallbacks: true}}` nested INSIDE `litellm_params`** reliably pins DeepSeek official. Config-level injection confirmed (not just request-level).
- Confirmed config-level works: put `extra_body` at 6-space indent under `litellm_params`, NOT at model level (model-level `provider:`/`extra_body:` is ignored).

## Edits already applied to /Users/matt/projects/ai-os/litellm/config.yaml
Backup: `/Users/matt/projects/ai-os/litellm/config.yaml.bak-2026-08-10` (restore point). YAML validated, 44 models intact.
1. All 5 flash entries (`deepseek-v4-flash`, `-high`, `-medium`, `-low`, + `haiku` alias): model → `openrouter/~deepseek/deepseek-v4-flash-latest`.
2. All 9 deepseek entries: dead model-level `provider:` block replaced with working `extra_body: {provider:{order:[DeepSeek],allow_fallbacks:true}}` inside `litellm_params`.
3. Fixed `deepseek-v4-pro-low`'s stray `sort: throughput` → same DeepSeek pin.
4. `v4-pro` model strings left as-is (only flash was asked to go latest), but all pro entries got the DeepSeek-official pin.

Sanity checks passed: 0 residual `    provider:` blocks, 0 residual `sort: throughput`, YAML parses, model_list count = 44.

## NEXT STEPS (do these in order in the new thread)
1. **Restart the LiteLLM proxy** (most important — the edit is inert until reload):
   - Try: `la restart agent-litellm`  (tmux session name is `agent-litellm`)
   - Or: restart the process running `/Users/matt/projects/ai-os/litellm/run_litellm.sh` → `litellm --config config.yaml --port 8082`. The launcher sources `~/.zshrc` for OPENROUTER_API_KEY.
2. **Verify on the LIVE proxy** that a deepseek call now returns `provider: DeepSeek`:
   - `curl -s http://127.0.0.1:8082/v1/models | grep deepseek` → should list the flash+pro variants.
   - POST `{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"Reply OK"}],"max_tokens":8}` to `http://127.0.0.1:8082/v1/chat/completions` and check the `provider` field in the response == `DeepSeek`. (Do NOT check the `provider` key existence in config — it's now `extra_body`.)
3. If verification fails, confirm the running config path is `/Users/matt/projects/ai-os/litellm/config.yaml` via `lsof -p <pid> | grep cwd` and re-check indentation of `extra_body` (must be 6-space, inside `litellm_params`).

## Deliberately out of scope (known leftovers — decide if you want them)
- **Zed** (`~/.config/zed/settings.json`): agent/inline models already use `~deepseek/deepseek-v4-flash-latest` via OpenRouter (good on "latest") but do NOT pin DeepSeek official provider — can still route to resellers. claude-acp server uses `deepseek-v4-pro-high`.
- **Hermes MoA Deepseek preset** (`~/.hermes/config.yaml` lines ~127-144): uses `deepseek-v4-pro`/`deepseek-v4-flash` via provider `openrouter`, NO `~latest` alias and NO DeepSeek-official pin. Needs separate handling (verify whether Hermes MoA forwards `extra_body` — uncertain).
- **Hermes main session model** is `deepseek/deepseek-v4-flash` via OpenRouter (this thread's own model) — also not pinned to DeepSeek official.

## Test artifacts (cleanup optional)
- `/Users/matt/projects/ai-os/tmp/test-litellm-config.yaml.bak` and `./tmp/litellm-test.log.bak` (throwaway :8099 proxy test). Safe to remove when done; use `mv ... ~/.Trash/` per house rules.