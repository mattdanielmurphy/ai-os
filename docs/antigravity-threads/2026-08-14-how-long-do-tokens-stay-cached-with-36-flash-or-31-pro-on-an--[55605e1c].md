---
title: "how long do tokens stay cached with: 3.6 flash or 3.1 pro on Antigravity,..."
date: "2026-08-14"
conversation_id: "55605e1c-d80c-4ac1-8190-0adc925e4279"
source: "antigravity"
---

# how long do tokens stay cached with: 3.6 flash or 3.1 pro on Antigravity,...

## User

how long do tokens stay cached with: 3.6 flash or 3.1 pro on Antigravity, deepseek v4 flash on claude code on openrouter via litellm, and ... idk anything else you can think that's relevant.
gemini.google.com threads actually that would be good to know.
perplexity.com threads.
Oh!
And hermes agent threads too.
I suspect it's all basically the same answer lol

---

## Assistant

## Perplexity — 01:17 AM

Good news: your suspicion is *wrong* — the retention windows actually vary a lot depending on whether you're talking about **backend prompt/KV caching** (a cost/latency optimization) versus **thread/chat history storage** (how long your conversation is kept at all). These are two different mechanisms that people often conflate.

Backend token (KV) caching — dev/API side
Setup	Cache TTL
Setup	Cache TTL
Gemini 3.6 Flash / 3.1 Pro via Antigravity (Gemini API)	Explicit caching defaults to **60 min**, no fixed max (can extend, effectively up to ~24h on Vertex); implicit caching (auto, on by default for 2.5+ models) doesn't expose a TTL at all — it's opportunistic 
google
+2

DeepSeek V4 Flash (native, or via Claude Code → OpenRouter → LiteLLM)	Automatic, no config needed. DeepSeek's own disk-based prefix cache says unused entries are cleared **"usually within a few hours to a few days,"** best-effort, no guaranteed hit rate or fixed number 
api-docs.deepseek
+2

Hermes Agent (Nous Research)	Config-driven: **5 minutes default**, extendable to **1 hour** for Claude models via Anthropic-style `cache_control` breakpoints (native Anthropic, OpenRouter, Nous Portal). Falls back to 5 min automatically if routed through Qwen/DashScope, which caps at 5 min regardless 
hermes-agent.nousresearch
+1

(For reference) Anthropic/Claude via OpenRouter generally	5 min default, 1 hour optional (costs more to write) 
openrouter

So on the pure caching side: Gemini's is the longest by default (1h), DeepSeek is vague/best-effort (hours-to-days but not guaranteed to survive that long if idle), and Anthropic-family (including Hermes) is short by default (5 min) unless you explicitly opt into the 1-hour tier.

Thread/chat history storage — consumer side

This is a totally different thing (not token caching, but persistence of the conversation itself):

**gemini.google.com threads**: the *active* working context is aggressively pruned to a sliding window (users report effective limits around 32K tokens even though the model technically supports 1M) — so functionally the model "forgets" much sooner than the cache TTL numbers above would suggest. Separately, chat *storage* in your account persists per your Activity setting, defaulting to auto-delete after **18 months** (configurable to 3, 36 months, or never).
support.google
+3

**perplexity.com threads**: signed-in threads are stored **indefinitely** in your Library until you delete them; logged-out threads expire after **14 days**; incognito threads after **24 hours**.
perplexity
+1

Bottom line

Not "basically the same answer" — dev-side caching windows range from 5 minutes to a few days, and consumer thread storage ranges from 24 hours to indefinite/18 months, and they measure completely different things (cost-saving cache reuse vs. how long your chat log sticks around).

---

## User

Why would I be talking about thread storage?
I'm talking about: if I have a project, will leaving it for >24 hrs mean resuming a thread is a bad idea because none of that thread will be cached when I send a new prompt in it?

---

## Assistant

## Perplexity — 01:17 AM

Ah, got it — you're asking a practical question: **does letting a project thread sit idle for 24+ hours mean your next prompt eats a full "cold" (uncached) reprocessing of the whole history, rather than just paying/waiting for the new bit?** Yes, for every setup you listed, 24 hours is way past the cache-expiry window, so you're right to expect a full cache miss on resume — but that only affects *cost/latency*, not whether the thread still works.

What happens on resume after >24h idle
Setup	Cache window	After 24h idle
Gemini 3.6 Flash/3.1 Pro via Antigravity	Explicit cache TTL default 60 min (extendable); implicit cache is opportunistic, no long persistence	Cache long expired — full reprocess of prior context as fresh input tokens
DeepSeek V4 Flash (Claude Code → OpenRouter → LiteLLM)	Disk cache, "cleared usually within a few hours to a few days" of disuse	Could go either way at 24h — sometimes still warm, sometimes not, since it's best-effort with no guarantee 
google

Claude/Anthropic-family (incl. Hermes Agent default)	5 min default, 1h if you opt into extended caching	Definitely cold — 24h is 24-288x longer than even the extended tier 
google
+2
The important part: it's not "bad," just more expensive/slower

Coming back to a stale thread doesn't corrupt anything or make the model forget — the full conversation history still gets resent to the model as normal input tokens. The only consequence is:

**Cost**: you pay full input-token price for the entire prior context instead of the discounted cached-read rate (e.g., Anthropic-style caching is typically ~90% cheaper per token on a hit).
antigravitylab

**Latency**: first response after resuming is slower because the model has to reprocess everything from scratch instead of reusing a stored KV cache.
google

As Anthropic's own Claude Code team put it: idling a session past the cache window just means your next message is a "full cache miss, all N messages" — the conversation itself is unaffected.
google

Practical takeaway for your workflow

If you're optimizing for cost/speed on a long-running coding project, treat threads like a "keep it warm or accept the reset fee" tradeoff:

Sub-5-minute gaps: cheap everywhere.

5 min–1 hour: cache miss on Anthropic/Hermes-style setups; still likely fine on Gemini's default 60-min window.

>1 hour to 24h+: essentially guaranteed full reprocessing cost across all of these, with DeepSeek being the only wildcard that *might* still hit.

So resuming after a day isn't "a bad idea" functionally — it'll just cost roughly like starting fresh with all that history pasted in, rather than the cheap continuation rate.

---

## User

omg!
I just had a great idea.
I'm going to build in a way for, when I send a message in an old thread, it'll automatically just capture a highlevel summary of that thread and create a new fresh thread with that summary as context so I never have to worry about this.

---

## Assistant

## Perplexity — 01:17 AM

Good news: you're reinventing something that already exists and is well-proven — this pattern is exactly what Claude Code's `/compact`, Hermes Agent's context compression, and most serious coding agents do. Worth knowing what's already been built and where the trade-offs bite, before you build your own version.

The pattern already has a name

This is called **context compaction/compression**: summarize the older part of a conversation, discard the verbatim transcript, and continue with the summary standing in for history. Claude Code does it via `/compact` (manual or auto-triggered near context limits), and Hermes Agent does it automatically with a more elaborate pipeline.
code.claude
+2

How Hermes does it (closest to what you're describing)

Hermes' implementation is a good reference design since it's open-source and well-documented:

**Head/middle/tail split**: the system prompt + first exchange (head) and the most recent ~20K tokens (tail) are kept verbatim; only the **middle** gets summarized.
dev
+1

**Cheap pre-pass first**: duplicate/verbose tool outputs get deduplicated and truncated *before* any LLM summarization call, so you're not paying a big model to summarize junk.
fp8

**Dedicated summarizer model**: a separate, often cheaper/faster model (e.g., Gemini Flash or a small Qwen) does the summarization, not your main agent model — this avoids the primary model choking on a huge "summarize yourself" task.
datacamp
youtube

**Iterative re-compression**: if you compact again later, it updates the *previous* summary rather than re-summarizing from scratch.
hermesbible

**Triggered proactively at a threshold** (e.g., 50–85% of context capacity), not only reactively on overflow.
datacamp
youtube

What to watch for in your own version

**Losing exact detail**: summaries keep intent/decisions/file changes but drop verbatim tool outputs and exact code snippets read earlier — the model can't "re-read" something it only has a paraphrase of.
code.claude

**Anti-hijack instructions**: Hermes explicitly appends an instruction block to the summary to prevent injected/malicious content in old messages from being reinterpreted as new instructions when it gets folded into a fresh context.
youtube

**Anti-thrashing guard**: don't compact on every message — Hermes stops compressing further if two consecutive passes save less than ~10%, to avoid wasting calls on marginal savings.
fp8

**Tail protection is token-budget based, not message-count based** — so a few huge tool-output messages don't accidentally eat your whole "recent" window .

For your specific caching concern

This directly solves your original worry: since compaction produces a **fresh, short context**, resuming after 24h+ idle means the new thread reprocesses a small summary, not the entire stale history — so you avoid the "full cache miss on a huge context" cost problem entirely, by design.
hermes-agent.nousresearch

If you want, I can help sketch the actual head/middle/tail + summarizer-call logic for your project's stack.

---

## User

wait a second.
In Hermes/Antigravity/Claude Code...
If you resume a thread after an hour of dormancy, (or even 24 hours), does that agent literally scoop up the ENTIRE token thing verbatim that *was* cached, or does it get a summary?

---

## Assistant

## Perplexity — 01:17 AM

Good question — the answer is **verbatim, always**. Nothing gets automatically summarized just because the cache expired. The cache is purely a cost/speed shortcut sitting *underneath* the real, full transcript — the transcript itself is untouched.

What actually happens on resume

**The full conversation is still stored** — on your machine (Claude Code, Hermes CLI) or in the session store — exactly as it was, message by message .

**When you send a new prompt, the client resends the entire verbatim transcript** to the model as input. The cache is just a mechanism the *provider's backend* uses to skip recomputing the internal KV-representation of tokens it's seen recently — it never changes what data gets sent.
news.ycombinator

If the cache is cold (expired), that whole resend is billed/processed at **full input-token price and full latency**, rather than the cheap cached-read rate. Nothing is lost, dropped, or compressed — you just pay the "cold" cost instead of the "warm" cost for identical content.
hermes-agent.nousresearch

Anthropic's Claude Code lead put it plainly: "You already have the data on your own machine, and that 'upload and restore' process is exactly what is happening when you restart an idle session" .

Where summarization *does* enter — and it's a separate, opt-in system

Summarization (compaction) only happens when a **different mechanism** decides the transcript itself is getting too big for the context window — not because the cache went cold:

**Hermes**: `ContextCompressor` fires automatically at 50% of context capacity (configurable), regardless of idle time. A 24-hour-old thread that's still short won't get touched; a 20-minute-old thread that's ballooned with huge tool outputs will .

**Claude Code**: `/compact` is manual, or auto-triggered near the context limit — again tied to size, not time .

These two systems (cache TTL vs. compaction trigger) are independent. Cache expiry is about *cost*; compaction is about *fitting in the context window*.

So to directly answer it

Resuming after 1 hour or 24 hours: the agent scoops up the **entire verbatim history**, not a summary — it's just that the provider has to reprocess all of it at full price instead of pulling a shortcut from its own cache. Your earlier compaction idea is a legitimate way to *reduce* the size of what gets resent, but it's a separate feature you'd have to build/trigger yourself — it doesn't happen automatically as a side effect of the cache lapsing.

---

## User

ok so I want to set up a system so that resuming a thread is never a bad choice economically (aka when the cache is expired, automatically hand-off a summary instead of actually resuming the thread).
Can you just describe that so I can pass it off to my agent to add as a plan

---

## Assistant

## Perplexity — 01:17 AM

I've put together the full design doc as a Markdown file you can hand straight to your agent — it covers the activity tracker, the pre-send TTL gate, the summarization/handoff step, guardrails against over-triggering, and a config surface for tuning it per provider.

The core mechanism

The trick is turning "is the cache cold?" into a purely mechanical check *before* sending, rather than something decided by an LLM call:

Track `last_message_at` per thread plus which provider/model it's using.

Compare `idle_time` against that provider's cache TTL (with a safety margin, since TTLs aren't guaranteed exactly).

If still warm, send normally. If cold, silently summarize the old thread with a cheap model, spin up a fresh thread seeded with that summary, and redirect the message there instead.

Key guardrails baked in

Skip compaction for threads that are already small — reprocessing a 2K-token thread cold costs almost nothing, so don't waste a summarization call on it.

Cap chained handoffs so you're not eventually summarizing a summary of a summary of a summary with no ceiling.

Keep summarizer output free of large verbatim code/tool dumps — reference that they existed rather than re-embedding them, to keep the new thread genuinely cheap.

This is fully provider-agnostic client-side orchestration — it sits in front of Antigravity, Claude Code/OpenRouter/LiteLLM, and Hermes identically, since all it needs is a timestamp, a TTL lookup, and one summarization call.

## Perplexity — 01:17 AM

Cache-Aware Thread Handoff — Design Plan
Goal

Never let a resumed thread pay full "cold" reprocessing cost. If the provider's
prompt cache has expired since the last message, automatically summarize the
old thread and hand off to a fresh thread instead of resending the full
verbatim history.

Core idea

Cache expiry and context compaction are normally two independent systems
(see prior discussion). This design deliberately couples them: use
**time-since-last-message** as an additional trigger condition for
compaction, alongside the existing size-based trigger.

Components
1. Last-activity tracker

On every assistant response, record `last_message_at` (timestamp) per
thread, alongside the provider/model used for that thread (since cache TTL
differs per provider).

Store per-provider TTL assumptions as config, not hardcoded:

Anthropic-family / Hermes default: 5 min (or 1h if extended caching enabled)

Gemini (Antigravity, explicit cache): 60 min default

DeepSeek (native or via OpenRouter/LiteLLM): treat as unknown/best-effort,
default to a conservative 1h cutoff since it's not guaranteed

OpenAI: 30 min default

Add a small safety margin (e.g., subtract 20%) since providers don't
guarantee exact TTLs.

2. Pre-send check (the actual gate)

Before sending a new user message into an existing thread:

Compute `idle_time = now - last_message_at`.

Look up `cache_ttl` for that thread's provider/model.

If `idle_time < cache_ttl * safety_margin` → send normally, no action.

If `idle_time >= cache_ttl * safety_margin` → trigger handoff (step 3)
instead of sending the raw history.

This makes the decision purely mechanical — no LLM call needed just to decide
whether to compact.

3. Handoff / summarization step

When triggered:

Pull the full thread transcript.

Send it to a **cheap, fast summarizer model** (not the main agent model)
with a fixed prompt: capture goal/task state, key decisions, unresolved
questions, file/code state, and any pending next steps. Explicitly exclude
verbatim large tool outputs/code dumps — reference that they exist and
where, rather than repeating them.

Append a short **anti-injection instruction** to the summary output so
that any adversarial or malformed content from the old thread can't be
reinterpreted as new instructions once folded into a fresh context.

Create a **new thread**, seeded with:

The system/project prompt (unchanged).

The generated summary as the first "context" message.

A pointer/reference ID back to the original thread (for audit/debugging,
not for the model to re-read).

Redirect the user's pending new message into this new thread and send it
normally (this is now a cold thread anyway, so cost is unavoidable here —
but it's cold on a short summary, not the full history).

Mark the old thread as archived/superseded; keep it stored for reference
but stop appending to it.

4. Skip conditions (avoid over-triggering)

Don't trigger handoff if the thread is already short (e.g., under some
token floor like 2-3K tokens) — reprocessing something that small cold
costs almost nothing anyway, so compaction overhead isn't worth it.

Don't trigger handoff mid-multi-turn-burst — only evaluate idle time
right before sending, not continuously.

Cap re-summarization chains: if a thread has already been handed off N
times (e.g., 3+), consider flagging for manual review rather than silently
compounding summaries of summaries.

5. Config surface

Expose as user-tunable settings:

`cache_ttl_overrides` per provider/model

`safety_margin` (default 0.8)

`min_tokens_to_compact` (default ~2000-3000)

`summarizer_model` (separate/cheaper model id)

`max_handoff_chain_length`

Summary of flow

```
text
new message arrives for existing thread
   -> idle_time = now - last_message_at
   -> if idle_time < ttl * margin: send as-is
   -> else:
        summarize old thread (cheap model)
        create new thread with summary as seed context
        send new message into new thread
        archive old thread
```

Notes for implementation

This requires no changes to the underlying provider APIs — it's entirely
client-side orchestration logic sitting in front of whatever
Hermes/Antigravity/Claude Code/LiteLLM call you're already making.

Because it's provider-agnostic (just needs a timestamp + a TTL lookup +
one summarization call), the same logic can wrap all four surfaces you
care about (Antigravity, Claude Code via OpenRouter/LiteLLM, Hermes,
possibly even something you build for Gemini/Perplexity-style threads).

## Perplexity — 01:17 AM

Cache-Aware Thread Handoff — Design Plan
Goal

Never let a resumed thread pay full "cold" reprocessing cost. If the provider's
prompt cache has expired since the last message, automatically summarize the
old thread and hand off to a fresh thread instead of resending the full
verbatim history.

Core idea

Cache expiry and context compaction are normally two independent systems
(see prior discussion). This design deliberately couples them: use
**time-since-last-message** as an additional trigger condition for
compaction, alongside the existing size-based trigger.

Components
1. Last-activity tracker

On every assistant response, record `last_message_at` (timestamp) per
thread, alongside the provider/model used for that thread (since cache TTL
differs per provider).

Store per-provider TTL assumptions as config, not hardcoded:

Anthropic-family / Hermes default: 5 min (or 1h if extended caching enabled)

Gemini (Antigravity, explicit cache): 60 min default

DeepSeek (native or via OpenRouter/LiteLLM): treat as unknown/best-effort,
default to a conservative 1h cutoff since it's not guaranteed

OpenAI: 30 min default

Add a small safety margin (e.g., subtract 20%) since providers don't
guarantee exact TTLs.

2. Pre-send check (the actual gate)

Before sending a new user message into an existing thread:

Compute `idle_time = now - last_message_at`.

Look up `cache_ttl` for that thread's provider/model.

If `idle_time < cache_ttl * safety_margin` → send normally, no action.

If `idle_time >= cache_ttl * safety_margin` → trigger handoff (step 3)
instead of sending the raw history.

This makes the decision purely mechanical — no LLM call needed just to decide
whether to compact.

3. Handoff / summarization step

When triggered:

Pull the full thread transcript.

Send it to a **cheap, fast summarizer model** (not the main agent model)
with a fixed prompt: capture goal/task state, key decisions, unresolved
questions, file/code state, and any pending next steps. Explicitly exclude
verbatim large tool outputs/code dumps — reference that they exist and
where, rather than repeating them.

Append a short **anti-injection instruction** to the summary output so
that any adversarial or malformed content from the old thread can't be
reinterpreted as new instructions once folded into a fresh context.

Create a **new thread**, seeded with:

The system/project prompt (unchanged).

The generated summary as the first "context" message.

A pointer/reference ID back to the original thread (for audit/debugging,
not for the model to re-read).

Redirect the user's pending new message into this new thread and send it
normally (this is now a cold thread anyway, so cost is unavoidable here —
but it's cold on a short summary, not the full history).

Mark the old thread as archived/superseded; keep it stored for reference
but stop appending to it.

4. Skip conditions (avoid over-triggering)

Don't trigger handoff if the thread is already short (e.g., under some
token floor like 2-3K tokens) — reprocessing something that small cold
costs almost nothing anyway, so compaction overhead isn't worth it.

Don't trigger handoff mid-multi-turn-burst — only evaluate idle time
right before sending, not continuously.

Cap re-summarization chains: if a thread has already been handed off N
times (e.g., 3+), consider flagging for manual review rather than silently
compounding summaries of summaries.

5. Config surface

Expose as user-tunable settings:

`cache_ttl_overrides` per provider/model

`safety_margin` (default 0.8)

`min_tokens_to_compact` (default ~2000-3000)

`summarizer_model` (separate/cheaper model id)

`max_handoff_chain_length`

Summary of flow

```
text
new message arrives for existing thread
   -> idle_time = now - last_message_at
   -> if idle_time < ttl * margin: send as-is
   -> else:
        summarize old thread (cheap model)
        create new thread with summary as seed context
        send new message into new thread
        archive old thread
```

Notes for implementation

This requires no changes to the underlying provider APIs — it's entirely
client-side orchestration logic sitting in front of whatever
Hermes/Antigravity/Claude Code/LiteLLM call you're already making.

Because it's provider-agnostic (just needs a timestamp + a TTL lookup +
one summarization call), the same logic can wrap all four surfaces you
care about (Antigravity, Claude Code via OpenRouter/LiteLLM, Hermes,
possibly even something you build for Gemini/Perplexity-style threads).

---
