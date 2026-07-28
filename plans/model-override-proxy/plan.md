# Plan: Model Override via `{MODEL=...}` in Proxy Prompt

## Goal

Allow Hermes' `delegate_task` to embed `{MODEL=model_alias}` in the prompt context string,
overriding the fixed `delegation.model` config value per-call. The proxy extracts and strips
the tag before any text reaches the LLM.

---

## Current State (what's already on disk)

`proxy.py` has **partial, broken work** that must be fixed rather than started from scratch:

- `import re` ✅ (line 2)
- `MODEL_OVERRIDE_RE = re.compile(r'\{MODEL=([^}]+)\}')` ✅ (line 79)
- `_resolve_model()` stub ⚠️ **broken** (lines 82–103) — see bugs below
- `run_agy_stream()` already calls `_resolve_model(messages, model_name)` ✅ (line 116)
- `run_agy_sync()` does **NOT** call `_resolve_model()` yet ❌ (line 177 builds prompt directly)

### Bugs in the existing `_resolve_model()` stub

1. **Duplicate dead loop**: The function has two identical `for msg in messages` loops (lines
   89–95, then 96–102). The second loop is unreachable dead code — the first loop always
   `return`s or falls through.
2. **Signature mismatch**: The docstring says it returns `(resolved_model, cleaned_messages)`
   but the actual return type is just `str`. Since `run_agy_stream()` assigns the return value
   to `model_name` (a scalar), this currently works by accident — but the docstring is wrong
   and misleading.
3. **In-place mutation of Pydantic models**: `msg.content = ...` mutates the Pydantic
   `Message` object directly. This works because Pydantic v1 allows field mutation by default,
   but it mutates the shared `request.messages` list in place, which could be a problem if
   the same request object is inspected after the call (e.g., for logging). Low risk, but
   worth noting.
4. **No fallback guard for `model_name == "subagent"`**: If the config is set to `subagent`
   and no `{MODEL=...}` tag is found in the prompt, `model_name` stays as `"subagent"`. The
   `agy` call then receives `--model subagent`, which is not a valid alias and will fail.

---

## Steps

### Step 1 — Fix `_resolve_model()` (replace lines 82–103)

Replace the entire broken stub with a correct implementation:

```python
def _resolve_model(messages: List[Message], model_name: str) -> str:
    """Scan messages (first match wins) for {MODEL=alias}, strip the tag in-place,
    and return the alias. Falls back to model_name if no tag found.

    Pitfall: if model_name is the 'subagent' placeholder and no tag is found,
    this returns 'subagent' — callers must guard against that (see Step 3).
    """
    for msg in messages:
        if msg.content and MODEL_OVERRIDE_RE.search(msg.content):
            match = MODEL_OVERRIDE_RE.search(msg.content)
            override = match.group(1).strip()
            # Strip tag from ALL messages so nothing leaks to the LLM
            for m in messages:
                if m.content:
                    m.content = MODEL_OVERRIDE_RE.sub("", m.content).strip()
            logger.info(f"[model-override] {model_name!r} → {override!r}")
            return override
    return model_name
```

Changes from the stub:
- Single outer loop finds the first match, inner loop strips the tag from **all** messages.
- `.strip()` on the alias handles `{MODEL= gemini-flash }` padding.
- Dead second loop removed entirely.
- `logger.info` still logs the override decision.

---

### Step 2 — Add `_resolve_model()` call to `run_agy_sync()` (line 177)

Current line 177:
```python
def run_agy_sync(messages: List[Message], model_name: str) -> dict:
    prompt = _build_agy_prompt(messages)
```

Change to:
```python
def run_agy_sync(messages: List[Message], model_name: str) -> dict:
    model_name = _resolve_model(messages, model_name)
    prompt = _build_agy_prompt(messages)
```

This mirrors what `run_agy_stream()` already does on line 116.

---

### Step 3 — Add `"subagent"` placeholder guard

After `_resolve_model()` returns, if `model_name` is still `"subagent"` (no tag found), the
`agy` invocation would receive `--model subagent` and fail. Add a guard in **both** functions,
immediately after the `_resolve_model()` call:

```python
if model_name == "subagent":
    logger.warning("[model-override] No {MODEL=...} tag found; falling back to agy default")
    model_name = "agy"   # omits --model flag entirely, uses agy's built-in default
```

The existing `cmd` block already handles `model_name == "agy"` by omitting `--model`:
```python
if model_name and model_name != "agy":
    cmd.extend(["--model", model_name])
```
So setting `model_name = "agy"` is the correct fallback idiom in this codebase.

---

### Step 4 — Add `"subagent"` to `AVAILABLE_MODELS` (lines 23–33)

The proxy's `/v1/models` endpoint and any validation logic references `AVAILABLE_MODELS`.
Add `"subagent"` so the placeholder is recognized:

```python
AVAILABLE_MODELS = [
    "agy",
    "subagent",          # ← ADD: placeholder used when {MODEL=...} override is expected
    "gemini-3.6-flash-low",
    "gemini-3.6-flash-medium",
    "gemini-3.6-flash-high",
    "gemini-3.1-pro-low",
    "gemini-3.1-pro-high",
    "claude-sonnet-4-6",
    "claude-opus-4-6-thinking",
    "gpt-oss-120b-medium",
]
```

---

### Step 5 — Update `~/.hermes/config.yaml`

```yaml
delegation:
  model: subagent    # was: gemini-3.6-flash-low
  provider: agy
```

> **Note:** This is `~/.hermes/config.yaml`, NOT `~/projects/ai-os/litellm/config.yaml`.
> These are two different files. The Hermes config controls what `model` field is sent in
> the OpenAI request body. Hermes requires a reload after this change.

---

### Step 6 — (Optional) Apply override to LiteLLM route

The LiteLLM path (`_proxy_to_litellm` / `_proxy_to_litellm_stream`) forwards `request.model`
to LiteLLM. Stripping `{MODEL=...}` tags from the messages before forwarding is safe and
desirable (prevents tag leaking to the LLM), but changing `request.model` for LiteLLM is more
complex (LiteLLM uses it for routing). Recommended approach if implementing:
- Strip tags from message content only (call `_resolve_model()` for the side-effect of stripping)
- Do NOT use the returned alias as the LiteLLM model (LiteLLM routing is separate)
- Mark as **low priority** — tool-bearing requests are the minority, and tags in tool prompts
  are unlikely.

---

## Edge Cases & Pitfalls

| Scenario | Risk | Handling |
|---|---|---|
| `model_name == "subagent"` with no tag | `agy --model subagent` → crash | Step 3 guard: fall back to `"agy"` |
| Tag in old turn of multi-turn thread | Stale model selected | First-tag-wins; instruct agents to put tag in current turn only |
| Multiple tags in same message | First `search()` match wins | Both are stripped by inner loop; only first alias used |
| Tag in `tool` or `tool_calls` role | Not scanned (`msg.content` only) | `ToolCall` objects have no `.content`; safe |
| Whitespace in alias: `{MODEL= x }` | `.strip()` on `match.group(1)` | Already handled in Step 1 |
| In-place mutation of Pydantic objects | Shared state issue | Pydantic v1 allows this; low risk since messages are per-request |
| Concurrent requests | Each request has its own `messages` list from Pydantic parsing | No shared state; thread-safe |
| LiteLLM path leaks tag to LLM | Tag appears in LiteLLM-forwarded content | Acceptable short-term; see Step 6 for optional fix |

---

## Verification

### 1. Unit test (no server needed)

```python
# Run from: ~/projects/ai-os/services/agy-proxy/
# python3 -c "..."
import sys; sys.path.insert(0, ".")
from proxy import _resolve_model, Message

# Tag extracted, stripped, first-wins
msgs = [
    Message(role="user", content="{MODEL=claude-sonnet-4-6} What is 2+2?")
]
result = _resolve_model(msgs, "subagent")
assert result == "claude-sonnet-4-6", repr(result)
assert "{MODEL" not in msgs[0].content, repr(msgs[0].content)

# No tag → returns default unchanged
msgs2 = [Message(role="user", content="plain prompt")]
assert _resolve_model(msgs2, "subagent") == "subagent"
assert msgs2[0].content == "plain prompt"

# subagent placeholder with no tag → guard in caller returns "agy" (not tested here, test in integration)

print("✅ _resolve_model tests passed")
```

### 2. Smoke test via curl (proxy must be running)

```bash
# Override to claude-sonnet-4-6
curl -s -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "subagent",
    "messages": [{"role":"user","content":"{MODEL=claude-sonnet-4-6} What is 2+2?"}]
  }' | jq -r '.choices[0].message.content // .choices[0].delta.content'

# Check proxy logs for: [model-override] 'subagent' → 'claude-sonnet-4-6'
# Check proxy logs for: agy stream cmd: ... --model claude-sonnet-4-6 ...

# No tag → fallback to agy default, no --model flag
curl -s -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"subagent","messages":[{"role":"user","content":"plain prompt"}]}' | jq .
# Proxy logs should NOT show --model subagent; should log the fallback warning
```

### 3. Confirm tag never reaches LLM

In the response body, check that `{MODEL=` does not appear anywhere in the assistant content.

---

## File Change Summary

| File | Change | Status |
|---|---|---|
| `services/agy-proxy/proxy.py` | Fix `_resolve_model()` (Step 1) | Broken stub exists, needs fix |
| `services/agy-proxy/proxy.py` | Add `_resolve_model()` call in `run_agy_sync()` (Step 2) | Missing |
| `services/agy-proxy/proxy.py` | Add `"subagent"` fallback guard in both agy functions (Step 3) | Missing |
| `services/agy-proxy/proxy.py` | Add `"subagent"` to `AVAILABLE_MODELS` (Step 4) | Missing |
| `~/.hermes/config.yaml` | Set `delegation.model: subagent` (Step 5) | Pending |
