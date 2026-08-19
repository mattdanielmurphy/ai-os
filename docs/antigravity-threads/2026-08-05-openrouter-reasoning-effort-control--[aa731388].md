---
title: "OpenRouter Reasoning Effort Control"
date: "2026-08-05"
conversation_id: "aa731388cbdb09ba"
source: "antigravity"
---

# OpenRouter Reasoning Effort Control

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-08-05 03:35 MDT-6] [context to this point is 0] with `deepseek/deepseek-v4-flash:nitro` I can force OR to give me no reasoning right?

But can I do :max or something?

talking about using Warp agents with openrouter

---

## Assistant

Based on the configuration shown in image_351024.png, you are setting up OpenRouter as a custom endpoint in Warp using the standard OpenAI API schema.

The `:nitro` suffix you appended to `deepseek/deepseek-v4-flash` is a valid OpenRouter modifier. It acts as a routing shortcut that automatically selects the provider with the highest throughput (fastest speed) for that specific model.

However, you cannot control reasoning effort directly through model name suffixes like `:max` or `:none`.

How OpenRouter Handles Reasoning Effort

OpenRouter controls reasoning behavior by accepting a specific `"reasoning"` object in the JSON payload of the API request, rather than through URL or model name modifiers.

If you had direct control over the API payload, you would pass the following parameters:

**To force NO reasoning:** Add `"reasoning": { "effort": "none" }` to the JSON body.

**To force MAX reasoning:** Add `"reasoning": { "effort": "max" }` to the JSON body, which allocates approximately 95% of the model's max tokens to reasoning.

The Limitation with Warp Agents

Because Warp's custom endpoint UI relies strictly on the standard OpenAI Chat Completions schema (Endpoint URL, API Key, and Model Name), it does not currently expose a way to inject custom OpenRouter-specific JSON objects like `"reasoning"` into the request body.

Until Warp introduces a feature to add custom payload parameters, or OpenRouter introduces specific model string suffixes for effort levels (they currently only offer `:thinking` to enable reasoning by default), you cannot override the default reasoning effort of `deepseek/deepseek-v4-flash:nitro` when querying it natively through Warp.

---

## User

[2026-08-05 03:36 MDT-6] [context to this point is 537] any idea what `deepseek/deepseek-v4-flash` would default to? med reasoning?

---

## Assistant

According to the official DeepSeek API documentation, for `deepseek-v4-flash`, thinking mode is enabled by default, and the default reasoning effort is **`high`**.

OpenRouter honors this default when routing requests to the underlying DeepSeek endpoint. Because Warp agents do not currently allow you to inject the custom `reasoning_effort` JSON parameter, any standard request you make through `deepseek/deepseek-v4-flash:nitro` will operate at that default `high` effort level.

Interestingly, DeepSeek's API Gateway has a behavioral quirk: if it detects a request coming from a complex agent environment—identified by a combination of tool definitions, session headers, and specific agent profile system prompts—it will automatically force the reasoning effort to `max`, regardless of the requested setting. However, because you are using Warp and OpenRouter, your requests likely lack the specific combination of headers and prompt signatures (like those sent by Claude Code or OpenCode) required to trigger this automatic `max` override.

Therefore, you can expect your Warp agent to run `deepseek-v4-flash:nitro` with **`high`** reasoning effort.

---
