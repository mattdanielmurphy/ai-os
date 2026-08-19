---
title: "I don't get it, Hermes has an \"iteration cap\" that makes threads become..."
date: "2026-08-14"
conversation_id: "9c744c81-b6fa-44a9-92d3-79f1df12e55b"
source: "antigravity"
---

# I don't get it, Hermes has an \"iteration cap\" that makes threads become...

## User

I don't get it, Hermes has an "iteration cap" that makes threads become useless even though there's not even that much context in it?
Why?

---

## Assistant

## Perplexity — 04:57 PM

The iteration cap and the context window are two completely separate limits — Hermes hits the iteration budget wall even though there's plenty of context room left because it's counting *tool calls*, not tokens.

Two independent limits

Hermes Agent tracks an `IterationBudget` per agent, separate from context/token usage. The default cap (`agent.max_turns`) is 90 iterations per conversation turn, where each iteration = one full LLM call plus tool execution. Your screenshot shows context at only 13% used (140k of 1M tokens), but that number is irrelevant to the iteration counter — Hermes stops the loop once it burns through its 90 (or configured) calls regardless of how much context headroom remains.
hermes-agent.nousresearch
+2

Why it exists at all

The cap is a safety/cost backstop, not a context-management tool. Complex tasks with lots of tool calls (file reads, config edits, verification steps) can burn through the budget fast even on a "simple" thread, because each read/write/check counts as one unit consumed via `IterationBudget.consume()`. It's designed to prevent runaway loops or infinite tool-call chains, not to reflect whether the thread still has useful context.
kenhuangus.substack

Why it feels dumb in your case

Earlier Hermes builds injected mid-task warnings at 70%/90% budget usage, but Nous Research actually removed that in April 2026 because it caused models to abandon complex tasks prematurely — meaning your thread hit the cap with **no warning at all**, which is exactly the jarring experience you had. Subagents get their own independent budgets (default 50), so delegated work doesn't even share the parent's pool, but the parent thread itself still hard-stops at its own cap once exhausted.
hermes-agent.nousresearch
+2

What you can actually do

Since context wasn't the bottleneck, the fix isn't compaction — it's raising the ceiling. You can bump `agent.max_turns` in your `~/.hermes/config.yaml` (or per-thread override) well above 90; guides suggest 150+ for deep exploration tasks, and there's no hard reason not to go higher for iteration-heavy debugging work like the DeepSeek config verification you were doing. Your handoff-file approach for resuming in a new thread is the right workaround in the meantime, since a fresh thread gets a fresh iteration budget independent of the old one.
kenhuangus.substack
+1
youtube

---

## User

I feel like it makes sense to say: max tool calls PER turn, but max tool calls PER thread is just stupid

---

## Assistant

## Perplexity — 04:57 PM

Your instinct is basically right — and looking at the actual design, Hermes's cap **is** per-turn, not a lifetime thread limit. The confusion is that in an agentic coding session, "one turn" can quietly become "the whole thread."

What the cap actually measures

`agent.max_turns` (default 500, formerly documented lower in some builds) bounds the iteration loop inside a single `run_conversation()` call — i.e., one user message and everything the agent does in response to it (tool calls, file edits, verification steps) before it hands control back to you. It is explicitly scoped as "the agent loop for **one conversation turn**," not the cumulative history of the thread.
hermes-agent.nousresearch
+1

Why it feels like a thread-wide kill switch

The catch is that when you give Hermes an open-ended task ("fix the config and verify it's working"), the agent treats that as one continuous turn and can burn through hundreds of tool calls — file reads, edits, shell checks — without ever handing back to you. So the 500-call budget gets consumed entirely within what is, from your perspective, a single request, and once it hits 100% the agent stops, does one final "grace call" to summarize, and returns. It's not that the thread accumulated calls across many messages; it's that one ambitious ask **was** the whole budget.
hermes-agent.nousresearch
+1

Why a per-turn design still makes sense

It's a safety backstop against runaway tool-call loops (an agent stuck retrying a failing command forever), not a context-usage proxy — that's why it's independent of your 13%-used context window.
heyrocky

Subagents spawned via `delegate_task` get their own separate budget (default 50), so a genuinely huge task can be broken into delegated chunks that don't share the parent's pool.
hermes-agent.nousresearch

The maintainers deliberately removed early 70%/90% warnings because injecting budget-pressure messages mid-task caused models to abandon complex work prematurely — so now you get zero warning until the hard stop.
heyrocky

The actual fix for your case

Since your task (verify config, restart proxy, confirm) needed hundreds of sequential checks in one go, the practical fix isn't philosophical — it's operational: either raise `agent.max_turns` in `~/.hermes/config.yaml` well past 500 for iteration-heavy debugging threads, or break the task into a `delegate_task` subagent for the file-verification grind so it draws from its own 50-call pool instead of the main thread's. The maintainers' own guidance is blunt about this though: "a larger budget is not a quality setting... measure why a long workflow consumes iterations before raising the ceiling" — worth checking whether Hermes was looping on something (like retrying a failed restart) rather than genuinely needing 500+ distinct steps.
hermes-agent.nousresearch
+1

---
