---
title: "Model Caching and Cost After Stale Threads"
date: "2026-08-14"
conversation_id: "b9466b589c36a139"
source: "antigravity"
---

# Model Caching and Cost After Stale Threads

## User

if a thread has gone stale, or at least I think it has because it's been, say, 20 hours since the last message, does it matter if I change models at that point since the cache is probably dead anyway? Or is it still cheaper to use the same model somehow?

---

## Assistant

**No, it does not matter, and there is zero financial advantage to sticking with the same model once the cache is expired.**

After 20 hours, the prompt cache on any major provider (Anthropic, OpenAI, Google) is completely dead. Processing the context history will cost standard full input pricing regardless of which model you pick.

Why Cache Expiration Resets the Slate

**Short Cache TTLs:** Prompt caching across providers relies on short-lived memory windows. Anthropic’s prompt cache TTL is **5 minutes** (refreshed on hit), OpenAI’s is typically **5 to 60 minutes**, and Gemini’s automatic cache is similarly short-lived. At 20 hours, your prompt has long been evicted from the GPU context cache.

**Stateless API Nature:** LLM APIs do not retain a "discounted background state" for old sessions. When a cache is cold, the provider's servers must re-tokenize and run the prefill transformer pass over your entire chat history from scratch.

What Actually Determines Cost When Resuming

Because the cache is cold, the cost to re-process your context is determined strictly by two factors:

**The Model's Base Input Rate:**

**Switching to a smaller/cheaper model** (e.g., Claude 3.5 Haiku, GPT-4o-mini, or Gemini Flash) will be **significantly cheaper** than staying on a flagship model, even though you are loading the full history cold.

**Staying on a flagship model** (e.g., Claude 3.5 Sonnet, GPT-4o) means paying full input rates for the entire historical context again.

**Tokenizer Differences:**

If you switch between different model families (e.g., Anthropic to OpenAI), the underlying tokenizer changes. The same text history might yield a slightly different total token count (±5–15%), but the base rate per million tokens is what truly dictates the price.

Bottom Line

Once a thread has gone cold, treat the existing chat history simply as a block of text tokens you are feeding into a fresh prompt. Choose your next model based strictly on the **complexity of the task ahead** and its **base input token price**, not on what model generated the previous messages.

---
