---
title: "Reasoning Effort Resets Token Cache"
date: "2026-07-27"
conversation_id: "6207933057eb48e6"
source: "antigravity"
---

# Reasoning Effort Resets Token Cache

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Note-Taking Directive: When asked to "make a note about this" OR if we discuss anything interesting or ideas about future projects, you MUST proactively output a JSON tool call to save it as a note, or update an existing note. The JSON must be inside a ```tool_call codeblock. Schema: {"tool":"save_note","args":{"title":"Note Title","content":"Markdown content...","update":false}}. The userscript will execute this automatically and save it to Development/Project Notes/.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-07-27 17:01 MDT-6] [context to this point is 0] does changing reasoning effort mid-thread reset token cache?

---

## Assistant

Short answer: **Yes, in almost all cases.** Changing the reasoning effort level mid-thread invalidates the prompt cache, forcing the model provider to re-process the entire conversation context.  
GitHub

Here is why that happens and how it behaves across different providers:

Why It Breaks the Cache

Prompt caching relies on an **exact prefix match** of the request parameters and system structure.  
Claude Code by Anthropic | AI Coding Agent, Terminal, IDE

**System Prompt / Template Changes:** Providers (like OpenAI and Anthropic) often pass reasoning effort parameters, internal thinking budget allocations, or altered chat templates near the system level at the top of the prompt payload. Changing this setting alters the hash of the prefix, destroying the cache match.  
Claude Code by Anthropic | AI Coding Agent, Terminal, IDE
+ 1

**Keying by Config:** Many platforms segment cache pools by model state/configuration. A request sent to `model-x` with `reasoning_effort: high` hits a different logical cache key than `model-x` with `reasoning_effort: low`.

Provider Breakdown

**Anthropic / Claude:** Confirmed cache invalidation. Tools like Claude Code explicitly warn or prompt for confirmation before changing thinking/effort levels mid-session because doing so forces a full re-read of the context on the next turn.  
Claude Code by Anthropic | AI Coding Agent, Terminal, IDE
+ 1

**OpenAI (GPT-5 series / o-series):** Confirmed cache invalidation. Changing reasoning effort (`low`, `medium`, `high`) breaks the cached input history, resulting in a full cache miss for that turn.  
GitHub
+ 1

*Note:* Returning back to a *previously used* effort level in the same thread can sometimes hit the cache again if the prior cache entry hasn't expired (TTL usually 5–30 minutes).

Practical Takeaway

If you are working with a large context (e.g., 50k+ tokens), **avoid toggling reasoning levels for single quick questions** mid-thread. You will pay full price for re-processing the input tokens instead of getting the 90%+ prompt cache discount.

If you just need a quick, low-effort answer while keeping a heavy context intact, it is generally much cheaper to spin up a sub-agent or separate thread with only the relevant excerpt than to switch the main thread's effort setting down and back up.

---

## User

[2026-07-27 17:01 MDT-6] [context to this point is 741] fuck!

That doesn't seem like it has to be the case to me

---

## Assistant

It definitely *feels* like unnecessary overhead, but it comes down to how these models and infrastructure are actually built under the hood.

There are two distinct reasons why changing that parameter breaks the cache—one is a strict technical limitation, and the other is a systems architectural choice:

1. The Dynamic System Prompt Problem (Technical)

Prompt caching (like KV caching in transformer models) requires an exact sequence match of tokens from index `0` up to the end of the context.

When you change a setting like reasoning effort, API proxies and API backends don't just pass a bare metadata toggle to the model. They inject hidden system instructions, token budget parameters, or formatting tags directly into the root/system prompt area (e.g., `<thinking_budget=high>` or specialized prefix tags). Because those changes happen right at the beginning of the context payload, the cryptographic hash of the input changes at token index zero. The KV cache loader looks at the sequence, sees a mismatch on the system payload, and immediately throws out the cached key-value states for the remaining tens of thousands of tokens.

2. Physical GPU Routing (Architectural)

Different reasoning effort levels often route your request to entirely separate hardware clusters or execution pathways optimized for distinct latency and compute profiles.

**High reasoning effort** requests are routed to nodes configured for extended sampling loops, sequential token generation, and deep graph searches.

**Low reasoning effort** requests are routed to fast, throughput-optimized inference nodes designed for quick single-pass responses.

Because the GPU nodes physically holding your KV cache in VRAM during turn N−1 are not the same server nodes handling the fast low-effort response on turn N, the cache isn't accessible across that boundary.

It is a frustrating limitation of current inference engine architectures. The model host would need to implement prefix-agnostic KV-cache stitching or decoupling parameter metadata from the input token stream entirely to solve it—something none of the major providers have prioritized over raw inference scaling yet.

---
