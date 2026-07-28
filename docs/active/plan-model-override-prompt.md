# Plan: Model Override via `{MODEL=...}` in Proxy Prompt

## Background

Hermes' `delegate_task` tool sends requests to the agy-proxy (FastAPI on port 8080) with a single fixed `model` field from `delegation.model` in `config.yaml`. This field cannot be changed at runtime — requires a Hermes reload.

The agy-proxy already uses the `model` field to set `--model $model_name` when calling `agy --print`. But since it's fixed in config, every subagent uses the same model.

**Solution:** Embed `{MODEL=model_alias}` in the prompt text itself. The proxy scans messages for this tag, extracts the model alias, strips the tag from the content (so the LLM never sees it), and uses the alias as the real `--model` argument.

**Usage:** When I call `delegate_task`, I include `{MODEL=claude-sonnet-4-6}` in the `context` string. The proxy picks it up. `delegation.model` in config can be set to a placeholder like `subagent`.

## Current Proxy Architecture

The proxy lives at `~/projects/ai-os/services/agy-proxy/proxy.py` (354 lines, FastAPI + Pydantic).

### Route selection
- Requests WITH `tools` in the body → forward to LiteLLM at `http://127.0.0.1:8082/v1/chat/completions`
- Requests WITHOUT `tools` → route to `agy --print` CLI via one of two paths

### Two agy paths
Both are almost identical. They receive `(messages: List[Message], model_name: str)` and both need the override:

1. **`run_agy_stream()`** (lines 115-173) — Generator-based streaming. Builds prompt, spawns `agy --print` as subprocess, yields SSE chunks line-by-line.
2. **`run_agy_sync()`** (lines 176-198) — Simple `subprocess.run`, returns a dict.

### How `model_name` is used
In both functions:
```python
cmd = ["/Users/matt/.local/bin/agy", "--dangerously-skip-permissions", "--print"]
if model_name and model_name != "agy":
    cmd.extend(["--model", model_name])
cmd.append(prompt)
```

Valid model values (from the agy CLI perspective) are aliases like `gemini-3.6-flash-low`, `claude-sonnet-4-6`, etc.

### `_build_agy_prompt()` (lines 106-112)
Concatenates messages into a flat text prompt. Currently doesn't strip or modify content.

### `Message` schema (lines 59-63)
```python
class Message(BaseModel):
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
```

## What Needs to Change

### 1. Add `_resolve_model()` function
- Scan messages for `{MODEL=...}` regex
- Extract the alias, strip the tag from `msg.content` (mutate in-place so `_build_agy_prompt()` never sees it)
- Return the override model name, or the original if no tag found
- Log the override decision

### 2. Call `_resolve_model()` in both `run_agy_stream()` and `run_agy_sync()`
- Before `_build_agy_prompt()` — so the tag is already stripped from message content
- The resolved model name flows into the `--model` arg and into SSE response metadata

### 3. (Optional) Apply to LiteLLM route too
The LiteLLM path (`_proxy_to_litellm` / `_proxy_to_litellm_stream`) receives `request.model` but could also scan `request.messages` for the override. Less critical since tools require LiteLLM anyway, but nice for consistency.

### 4. Config update
In `/Users/matt/.hermes/config.yaml`, set:
```yaml
delegation:
  model: subagent
  provider: agy
```
This is a non-breaking placeholder — the proxy won't try to map `subagent` to a real model because `_resolve_model()` will override it from the prompt.

## Model Aliases (for reference)

From `~/.hermes/config.yaml` aliases:
- `agy/gemini-3.6-flash-low` → pass `gemini-3.6-flash-low`
- `agy/gemini-3.6-flash-medium` → pass `gemini-3.6-flash-medium`
- `agy/gemini-3.6-flash-high` → pass `gemini-3.6-flash-high`
- `agy/gemini-3.1-pro-low` → pass `gemini-3.1-pro-low`
- `agy/gemini-3.1-pro-high` → pass `gemini-3.1-pro-high`
- `agy/claude-sonnet-4-6` → pass `claude-sonnet-4-6`
- `agy/claude-opus-4-6-thinking` → pass `claude-opus-4-6-thinking`
- `agy/gpt-oss-120b-medium` → pass `gpt-oss-120b-medium`

Also available in the proxy's `AVAILABLE_MODELS` list (line 22-32): `agy`, `gemini-3.6-flash-low`, `gemini-3.6-flash-medium`, `gemini-3.6-flash-high`, `gemini-3.1-pro-low`, `gemini-3.1-pro-high`, `claude-sonnet-4-6`, `claude-opus-4-6-thinking`, `gpt-oss-120b-medium`.

## Existing (Partial) Work

I already added to the file on disk:
- `import re` on line 2
- `MODEL_OVERRIDE_RE = re.compile(r'\{MODEL=([^}]+)\}')` on line 79
- A broken `_resolve_model()` stub on lines 82-103 (duplicate loop, wrong iteration direction)
- `model_name = _resolve_model(messages, model_name)` on line 116 of `run_agy_stream()`

**`run_agy_sync()` does NOT have the call yet** (line 177 still builds prompt without resolving).

The existing `_resolve_model()` has bugs:
- Iterates all messages twice instead of just once
- Both loops iterate forward, the second is dead code
- No handling for `model_name == "subagent"` fallback (should fail gracefully if no override found and model is the placeholder)

## Plan Output Format

Write the plan to `~/projects/ai-os/plans/model-override-proxy/plan.md` following the `.hermes/plans/` convention:

```markdown
# Plan: Model Override via `{MODEL=...}`

## Goal
...

## Steps
1. ...
2. ...

## Verification
- ...
```

Include:
- Numbered steps with code snippets
- Edge cases (empty content, multiple messages with tags, streaming vs sync, LiteLLM route)
- Pitfalls (tag not stripped before LLM, `model_name == "subagent"` with no override, concurrent request safety)
- Verification steps (send test prompts, check logs for override message)
