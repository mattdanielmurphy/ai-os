# Restore LiteLLM for Warp (2026-10-27)

## 19:20 Warp can talk to OpenRouter directly

Matt asked to get LiteLLM running again on the VPS, hooked to OpenRouter, and connected to Warp, using the "Pareto frontier agent" (he remembered it as GPT-6 Luna).

---

### LiteLLM was on the Mac

The old LiteLLM proxy never ran on the VPS. It ran on the Mac as the launch agent `com.matt.agent.litellm` (port 8082, config `litellm/config.yaml`), and it was shelved on 2026-10-17 and switched off on 2026-10-21 (see `shelf/INDEX.md`). The VPS has no LiteLLM install and no Caddy route for one. The OpenRouter key line in `~/.zshrc` is also commented out, which is probably why the old routes stopped working.

---

### Warp needs a public URL

Warp's [custom inference endpoint](https://docs.warp.dev/agents/inference/custom-inference-endpoint.md) sends requests through Warp's servers, so `localhost` and private addresses are rejected. A Mac-only LiteLLM can't work with Warp. Warp lists OpenRouter itself as a compatible endpoint.

---

### Why skip LiteLLM

Pointing Warp straight at `https://openrouter.ai/api/v1` does the same job with no server to run, no public port to secure on the VPS, and no install (the LiteLLM image is over a gigabyte, and the VPS runs mail, Alby Hub and Minecraft). The project freeze also says to simplify rather than add. Rejected: LiteLLM in Docker on the VPS behind Caddy with a master key. It's only worth it if Matt wants one key for many tools or custom aliases/fallbacks.

---

### Pareto is a router

OpenRouter's model list has `openrouter/pareto-code` ("Pareto Code Router"): it picks from a shortlist of strong coding models ranked by Artificial Analysis coding scores. That matches "Pareto frontier agent". `openai/gpt-6-luna` is a separate model (OpenAI's fast, cheap GPT-6 tier), and `~openai/gpt-luna-latest` always points at the newest Luna. Both support tool calling. Not verified: which model the Pareto router actually picks today.

---

### Values for Warp

Warp > Settings, search "inference endpoint" (Agents > Warp Agent > Custom inference), add a model:
- Endpoint URL: `https://openrouter.ai/api/v1`
- API key: his OpenRouter key (he pastes it; agents never type keys)
- Model 1: `openrouter/pareto-code`, alias `pareto`
- Model 2: `openai/gpt-6-luna`, alias `luna`
Then pick the model directly in the picker (Auto models ignore custom endpoints). Switch with `/model pareto`.

---

### Untested

Not run end to end: agents can't enter API keys, so no request went through Warp yet. Undo: delete the custom model in Warp settings. Nothing on the VPS or Mac was changed.
