---
title: "OpenRouter Reasoning Parameter Control"
date: "2026-08-13"
conversation_id: "9d95173433bebdd0"
source: "antigravity"
---

# OpenRouter Reasoning Parameter Control

## User

you can send a reasoning level to deepseek-v4-flash with open router right?

What if I wanted to use reasoning none?

---

## Assistant

Yes. OpenRouter provides a unified `reasoning` parameter object (as well as top-level `reasoning_effort`) that translates directly across supported reasoning models like DeepSeek, OpenAI, and Anthropic.  
OpenRouter
+ 1

Setting `reasoning: { effort: "none" }`

When you explicitly pass `"none"` to OpenRouter, it disables the thinking/reasoning pass entirely. The model operates as a standard non-thinking model, skipping the chain-of-thought process and streaming the direct answer immediately.  
OpenRouter
+ 1

1. OpenRouter Unified Object (Recommended)
JSON

```
{
  "model": "deepseek/deepseek-v4-flash",
  "messages": [
    { "role": "user", "content": "Write a quick summary of REST APIs." }
  ],
  "reasoning": {
    "effort": "none"
  }
}

```

2. OpenAI SDK / Direct Top-Level Field

If you're using the standard OpenAI SDK routed through OpenRouter's base URL (`[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)`), you can pass `reasoning_effort`:

JSON

```
{
  "model": "deepseek/deepseek-v4-flash",
  "messages": [
    { "role": "user", "content": "Write a quick summary of REST APIs." }
  ],
  "reasoning_effort": "none"
}

```

What Happens When You Set `none`

**Latency Drops:** Skipping internal reasoning generation significantly cuts Time To First Token (TTFT) and overall completion time.

**Token Cost Drops:** You aren't billed for generated reasoning tokens (which are normally billed as output tokens).

**Sampling Parameters Re-enable:** Standard parameters like `temperature`, `top_p`, and `frequency_penalty` take full effect again (which upstream providers usually override or ignore while reasoning mode is active).  
DeepSeek

---

## User

what's a good default, do you reckon?

---

## Assistant

For general-purpose agentic workflows or code chat, **`low`** or **`medium`** is usually the sweet spot, but it depends entirely on whether you are using `deepseek-v4-flash` as a fast router or as an end-of-line executor.

The Breakdown

**`low` (Best for standard coding, tool execution, & structured tasks)**

**Why:** You get 80–90% of the reasoning quality while keeping Latency/TTFT low and avoiding token inflation. It handles schema validation, code edits, and standard instruction-following without burning cycles overthinking trivial logic.

**`none` (Best for simple text generation, fast transformations, or micro-agents)**

**Why:** If the prompt is straightforward (e.g., summarizing text, reformatting JSON, translating string keys), thinking overhead is just dead latency.

**`high` / `xhigh` (Best for deep algorithmic debug, multi-file refactoring, or math)**

**Why:** Flash models can occasionally go off the rails on edge-case logic when under-reasoned. Pushing effort to `high` forces a full chain-of-thought pass before execution.

Recommended Configuration Strategy

Instead of hardcoding a single default globally, pass it dynamically based on task type:

JSON

```
// Fast/cheap tier (Tool calling, text formatting, summaries)
{ "reasoning": { "effort": "low" } }

// Heavy tier (Complex debugging, architectural planning)
{ "reasoning": { "effort": "high" } }

```


If you must pick **one single default** across an entire codebase: go with **`low`**. It strikes the best balance between model capability and rapid time-to-first-token.

---

## User

how can I see on open router which of these are actually available?

---

## Assistant

OpenRouter exposes this programmatically via their API, as well as in their web playground and endpoint docs.  
OpenRouter

1. Programmatically via the API (Best for Dynamic Logic)

When you fetch the available models endpoint (`GET [https://openrouter.ai/api/v1/models](https://openrouter.ai/api/v1/models)`), OpenRouter includes a `reasoning` object on models that support reasoning configuration.

If you query that endpoint, the JSON response for a given model looks like this:

JSON

```
{
  "id": "deepseek/deepseek-v4-flash",
  "name": "DeepSeek V4 Flash",
  "reasoning": {
    "supported_efforts": ["xhigh", "high", "medium", "low", "minimal", "none"],
    "default_effort": "medium",
    "default_enabled": true,
    "supports_max_tokens": true,
    "mandatory": false
  }
}

```

What to look for in the metadata:

**`supported_efforts`**: An array listing exact values accepted by that specific model (e.g., `["high", "medium", "low", "none"]`). If `supported_efforts` is `null`, all gateway effort levels are accepted.  
OpenRouter
+ 1

**`mandatory`**: If `true`, the provider *requires* reasoning and will throw an error if you pass `effort: "none"`.  
OpenRouter

**`supports_max_tokens`**: Indicates whether you can pass exact token budget limits (`reasoning: { max_tokens: 2000 }`) instead of effort levels.  
OpenRouter

Quick `cURL` test:

You can check a specific model directly in your terminal using `jq`:

Bash

```
curl -s https://openrouter.ai/api/v1/models | jq '.data[] | select(.id == "deepseek/deepseek-v4-flash") | .reasoning'

```

2. Via the OpenRouter UI

If you want to quickly check on the web without writing code:

Go to `openrouter.ai/models` and click on the target model (or go directly to `openrouter.ai/deepseek/deepseek-v4-flash`).

On the right-hand panel, look under the **Parameters** table or open the **Playground** tab.

In the Playground settings sidebar, expand the **Reasoning / Thinking** controls. If effort controls are supported, you will see a dropdown slider listing the active effort levels (ranging from `xhigh` down to `none` or `disabled`).  
OpenRouter

---

## User

{

"id": "~deepseek/deepseek-v4-flash-latest",

"canonical_slug": "~deepseek/deepseek-v4-flash-latest",

"alias_target": {

"name": "DeepSeek: DeepSeek V4 Flash 0731",

"slug": "deepseek/deepseek-v4-flash-0731"

},

"hugging_face_id": null,

"name": "DeepSeek V4 Flash Latest",

"created": 1785606009,

"description": "This model always redirects to the latest model in the DeepSeek V4 Flash family.",

"context_length": 1048576,

"architecture": {

"modality": "text-\u003Etext",

"input_modalities": [

"text"

],

"output_modalities": [

"text"

],

"tokenizer": "Router",

"instruct_type": null

},

"pricing": {

"prompt": "0.000000079996",

"completion": "0.000000252",

"input_cache_read": "0.0000000252"

},

"top_provider": {

"context_length": 1048576,

"max_completion_tokens": null,

"is_moderated": false

},

"per_request_limits": null,

"supported_parameters": [

"frequency_penalty",

"include_reasoning",

"logit_bias",

"logprobs",

"max_tokens",

"min_p",

"parallel_tool_calls",

"presence_penalty",

"reasoning",

"reasoning_effort",

"repetition_penalty",

"response_format",

"seed",

"stop",

"structured_outputs",

"temperature",

"tool_choice",

"tools",

"top_a",

"top_k",

"top_logprobs",

"top_p"

],

"default_parameters": {

},

"supported_voices": [],

"knowledge_cutoff": null,

"expiration_date": null,

"links": {

"details": "/api/v1/models/~deepseek/deepseek-v4-flash-latest/endpoints"

},

"reasoning": {

"mandatory": false,

"default_enabled": true,

"supported_efforts": [

"max",

"high",

"low"

],

"default_effort": "high"

}

},

does that mean I call it like this: `openrouter/~deepseek/deepseek-v4-flash-latest`? I want to use latest v4 flash.

---

## Assistant

The string prefix depends on whether you are hitting the OpenRouter API directly or passing the model ID to a CLI/agent harness (like OpenClaw, Aider, or Cursor).

1. Direct OpenRouter API Request (cURL, SDK, or REST)

Do **not** include the `openrouter/` prefix when querying OpenRouter's native `[https://openrouter.ai/api/v1/chat/completions](https://openrouter.ai/api/v1/chat/completions)` endpoint. Use the exact `id` field from the JSON:

JSON

```
{
  "model": "~deepseek/deepseek-v4-flash-latest",
  "reasoning": {
    "effort": "low"
  },
  "messages": [
    { "role": "user", "content": "Hello world" }
  ]
}

```


The `~` tells OpenRouter to dynamically resolve the request to the target model in `alias_target` (`deepseek/deepseek-v4-flash-0731`).

2. Coding Harnesses / AGi / Client Frameworks

If you are setting this up inside an environment that routes through a multi-provider proxy (like OpenClaw or an ACP client), the harness uses `openrouter/` as a provider namespace:

Plaintext

```
openrouter/~deepseek/deepseek-v4-flash-latest

```

Key Things to Note in That Payload

**Reasoning Efforts:** Notice that for this specific model variant, the supported efforts are:

JSON

```
"supported_efforts": ["max", "high", "low"]

```


Passing `"medium"` or `"none"` on this specific alias may throw a validation error or fall back to default, as OpenRouter strictly exposes `max`, `high`, and `low` for it.

**`mandatory: false`:** You can safely omit reasoning parameters or disable thinking passes without breaking the request.

---

## User

i'm setting this up in my litellm config. I guess that's really what I need to check, huh?

Will this work?

---

## Assistant

Yes, it will work—with **two subtle LiteLLM config quirks** you need to account for:  
LiteLLM

**The Model Prefix (`openrouter/`):** You must prepend `openrouter/` to the model field in LiteLLM so it knows which provider endpoint to hit.  
LiteLLM

**Reasoning Effort Mapping:** In LiteLLM, pass `reasoning_effort` inside `litellm_params` (or `extra_body`).  
LiteLLM

*(Note: Since this specific alias supported `["max", "high", "low"]`, use `"low"` or `"high"` rather than `"medium"` or `"none"`).*

LiteLLM `config.yaml` Example
YAML

```
model_list:
  - model_name: v4-flash-fast
    litellm_params:
      # Must include 'openrouter/' prefix + the exact model ID
      model: openrouter/~deepseek/deepseek-v4-flash-latest
      api_key: os.environ/OPENROUTER_API_KEY
      # Pass reasoning effort directly
      reasoning_effort: low

  - model_name: v4-flash-heavy
    litellm_params:
      model: openrouter/~deepseek/deepseek-v4-flash-latest
      api_key: os.environ/OPENROUTER_API_KEY
      reasoning_effort: high

```

If LiteLLM Doesn't Forward `reasoning_effort` for OpenRouter

LiteLLM natively passes `reasoning_effort` to standard OpenAI/Anthropic routes, but OpenRouter sometimes prefers the nested `reasoning: { effort: "..." }` payload.  
LiteLLM

If LiteLLM drops the top-level field or OpenRouter ignores it, pass it explicitly under `extra_body` to force OpenRouter's native structure:

YAML

```
  - model_name: v4-flash-fast
    litellm_params:
      model: openrouter/~deepseek/deepseek-v4-flash-latest
      api_key: os.environ/OPENROUTER_API_KEY
      extra_body:
        reasoning:
          effort: low

```

Quick Verification via cURL (LiteLLM Proxy)

Once LiteLLM is running, test the route to confirm the alias resolves and passes reasoning properly:

Bash

```
curl http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "v4-flash-fast",
    "messages": [{"role": "user", "content": "Ping"}]
  }'

```

---
