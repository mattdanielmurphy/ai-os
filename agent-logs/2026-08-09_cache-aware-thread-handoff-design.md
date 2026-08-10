# Cache-Aware Thread Handoff — Design Plan

**Date:** 2026-08-09
**Status:** Design / proposal (not yet implemented)
**Owned by:** ai-os ($HOME/projects/ai-os)
**Related scripts:** `scripts/preflight.py`, `scripts/check_thread_bloat.py`, `scripts/gen_conversation_md.py`, `scripts/watch_transcripts.py`

---

## Motivation

A resumed thread pays full cold reprocessing cost if the provider's prompt cache has expired
since the last message. Hermes has auto-compaction, but Antigravity.app does not, and compaction
only triggers when a thread gets large — not when it goes dormant.

If you resume a thread after an hour (or 24h) of dormancy, the agent does **not** get a summary —
it re-ingests the **entire verbatim transcript** (cache is only a cost/speed shortcut underneath
the full, untouched transcript). Nothing auto-summarizes just because the cache expired.

`check_thread_bloat.py` already models when a thread is *large* enough to compact
(`T_hist_threshold = S + ((R-1)/M)*(T_sys + S)`). This design deliberately **couples cache expiry
with compaction**: add **time-since-last-message** as an *additional* trigger alongside the existing
size-based trigger.

## Goal

Never let a resumed thread pay full "cold" reprocessing cost. If the provider's prompt cache has
expired since the last message, automatically summarize the old thread and hand off to a fresh
thread instead of resending the full verbatim history.

## Core idea

Cache expiry and context compaction are normally two independent systems. This design couples
them: use **time-since-last-message** as an additional trigger condition for compaction, alongside
the existing size-based trigger.

---

## Components

### 1. Last-activity tracker
- On every assistant response, record `last_message_at` (timestamp) per thread, alongside the
  provider/model used (since cache TTL differs per provider).
- Store per-provider TTL assumptions as **config, not hardcoded**:
  - Anthropic-family / Hermes default: 5 min (or 1h if extended caching enabled)
  - Gemini (Antigravity, explicit cache): 60 min default
  - DeepSeek (native or via OpenRouter/LiteLLM): treat as unknown/best-effort, conservative 1h cutoff
  - OpenAI: 30 min default
- Add a small safety margin (e.g. subtract 20%) since providers don't guarantee exact TTLs.

### 1b. DYNAMIC safety margin (edge-case refinement)
The safety margin should NOT be a flat constant — it must scale with thread cost. The cost of
being *wrong* (a cold mis-ingest / huge re-ingest) grows with how much code the thread is likely
to keep ingesting as it continues. So:
- Small/short thread → few tokens at risk → use a **relaxed** margin (compact less eagerly; the
  cost of resending is low).
- Large/long thread → huge re-ingest at risk → use an **aggressive** margin (compact sooner, i.e.
  effectively a smaller effective TTL, so we never let a big thread go cold and unpaid).
- Concretely: `effective_margin = base_margin adjusted by T_hist` (the transcript token size that
  `check_thread_bloat.py` already computes). E.g. a stepwise or continuous curve — as
  `T_hist / T_hist_threshold` increases toward/over bloat, shrink `effective_margin` toward a
  floor (`min_margin`). There's always residual unknown, but this is a smart heuristic that ties
  the *conservatism of handoff* to the *cost of getting it wrong*.
- Config: `base_margin` (0.8), `min_margin` (e.g. 0.35), and a scaling curve driven by
  `T_hist` / `T_hist_threshold` from `check_thread_bloat.py`.

### 2. Pre-send check (the actual gate)
Before sending a new user message into an existing thread:
1. Compute `idle_time = now - last_message_at`.
2. Look up `cache_ttl` for that thread's provider/model.
3. If `idle_time < cache_ttl * safety_margin` → send normally, no action.
4. If `idle_time >= cache_ttl * safety_margin` → trigger handoff (step 3) instead of sending raw history.

Purely mechanical — no LLM call needed just to decide whether to compact.

### 3. Handoff / summarization step
When triggered:
1. Pull the full thread transcript.
2. Send it to a **cheap, fast summarizer model** (not the main agent model) with a fixed prompt:
   capture goal/task state, key decisions, unresolved questions, file/code state, pending next steps.
   Explicitly exclude verbatim large tool outputs/code dumps — reference that they exist and where.
3. Append a short **anti-injection instruction** to the summary so adversarial/malformed content
   from the old thread can't be reinterpreted as new instructions once folded into a fresh context.
4. Create a **new thread** seeded with:
   - The system/project prompt (unchanged).
   - The generated summary as the first "context" message.
   - A pointer/reference ID back to the original thread (for audit/debugging, not for re-reading).
5. Redirect the pending new message into this new thread and send normally (cold either way, but
   cold on a short summary, not the full history).
6. Mark the old thread archived/superseded; keep stored for reference, stop appending to it.

### 4. Skip conditions (avoid over-triggering)
- Don't trigger if the thread is already short (e.g. under ~2–3K tokens) — small cold reprocess
  costs almost nothing, so compaction overhead isn't worth it.
- Don't trigger mid-multi-turn-burst — only evaluate idle time right before sending.
- Cap re-summarization chains: if a thread has already been handed off N times (e.g. 3+), flag for
  manual review rather than silently compounding summaries of summaries.

### 5. Config surface
- `cache_ttl_overrides` per provider/model
- `safety_margin` (default 0.8)
- `min_tokens_to_compact` (default ~2000–3000)
- `summarizer_model` (separate/cheaper model id)
- `max_handoff_chain_length`

## Summary of flow
```
new message arrives for existing thread
   -> idle_time = now - last_message_at
   -> if idle_time < ttl * margin: send as-is
   -> else:
        summarize old thread (cheap model)
        create new thread with summary as seed context
        send new message into new thread
        archive old thread
```

## Notes for implementation
- No changes needed to provider APIs — entirely client-side orchestration in front of whatever
  Hermes/Antigravity/Claude Code/LiteLLM call you're already making.
- Provider-agnostic (timestamp + TTL lookup + one summarization call), so the same logic can wrap
  all surfaces: Antigravity, Claude Code via OpenRouter/LiteLLM, Hermes.
- In ai-os, the natural home is alongside `preflight.py` (which already gates each turn) and
  `check_thread_bloat.py` (which already provides the token-size compaction signal). The
  `last_message_at` tracker could be added to `gen_conversation_md.py` / `watch_transcripts.py`
  bookkeeping since they already watch the transcript.jsonl.

## Related / broader goals (see separate note)
- Global cross-project prompt/transcript sync so the same thread can be recognized across
  Antigravity.app, Hermes, and project forks.
- Auto-generated `Discussions.html` per project (every prompt kept, code folded, replies summarized).
