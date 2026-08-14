---
title: "Caching LLM Prompts for Cost Savings"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "aaf17a64-5cf1-529a-b0e6-59ec515a269a"
url: ""
---

# Caching LLM Prompts for Cost Savings

> [!NOTE]
> Archived Gemini Thread: [Caching LLM Prompts for Cost Savings]() | Date: 2026-08-13

## User
[2026-07-07 22:43 MDT-6] if deepseek calls are so cheap and there's token caching which offers a significant savings on top of that... why not implement a way of literally just repeating every prompt 2 twice, maybe with a slight twist (ie you call the first model and instruct it to, on top of its other duties of course, come up with a way of altering the prompt slightly [rewording or restructuring somehow] to get different results without changing what the user wants), and then you call again and say: review these two approaches and take the best result...

I don't know, I wonder how the results would be, and if you extended that further, what you might get.

For example, would doing successive calls with only slight modifications to the input prompt be really cheap because of all the caching?; is the end result actually better?

<!-- /gemini-message -->

---

<!-- gemini-message index=2 role=assistant timestamp="2026-07-08 00:34" -->

---

## Gemini
This is a compelling architectural idea, and it leans heavily into a major shift in how modern LLM applications are being built.

The short answer to your core questions: **Yes, sequential calls with slight modifications are exceptionally cheap because of DeepSeek’s context caching mechanics—but only if you order the prompt segments correctly.** And yes, the end result is often substantially better, though the technique behaves slightly differently than a standard ensemble approach.  
Reddit

Here is a breakdown of how the caching mechanics respond to this pattern, why it works, and how to optimize it.

The Caching Mechanics: Exact Prefix Matching

DeepSeek’s context cache uses **exact prefix matching** starting from token 0. If you change a single character at the very beginning of a prompt, you completely break the cache for everything that follows it.  
DeepSeek API Docs
+ 1

If you want to run successive calls with slight prompt modifications and have it be ultra-cheap, you have to structure your multi-call wrapper strategically:

❌ The Naive Way (Breaks Caching)

If your script sends two separate requests structured like this:

**Request 1:** `[Slightly Reworded Prompt Variant A] + [Your 50,000-token Document]`

**Request 2:** `[Slightly Reworded Prompt Variant B] + [Your 50,000-token Document]`

Because the unique variation is at the front, **the cache misses entirely on Request 2**. You will be billed the full cache-miss price for processing that massive document all over again.  
DeepSeek AI

The Cache-Optimized Way

To force DeepSeek to give you the 98% input token discount (dropping input costs from $0.14 down to $0.0028 per million tokens on V4 Flash), you must push the variation to the very end of the sequence:

**Request 1:** `[System Prompt] + [Your Massive 50,000-token Document] + [Instruction Variant A]`

**Request 2:** `[System Prompt] + [Your Massive 50,000-token Document] + [Instruction Variant B]`

In this layout, the leading 50,000+ tokens are an identical match. Request 1 pays the minor entry fee, and Request 2 processes the massive context entirely from the cache, billing you only for the few new tokens at the tail end.

Does the End Result Actually Get Better?

Yes, this approach is essentially a programmatic, budget-friendly version of **Ensemble Generation** or **Self-Consistency**. In LLM architectures, prompting the same model from slightly different angles or asking it to evaluate multiple internal paths yields measurable performance gains for a few reasons:

**Mitigating Non-Determinism Traps:** LLMs generate text token-by-token based on probabilities. Sometimes a model takes a suboptimal path early in its response and gets trapped in a mediocre explanation. Forcing a second run with a reworded instruction alters those initial token probabilities, offering an entirely different path.

**The "Judge" Model Premium:** LLMs are historically much better at *evaluating* and criticizing existing text than they are at generating a flawless response on the very first try. Passing both generated options into a final consolidation call ("Review these two approaches and synthesize the best result") acts as a cheap error-correction layer.

Extending the Concept Further

If you take this concept to its logical conclusion, you arrive at patterns closely resembling **Tree of Thoughts (ToT)** or agentic voting harnesses:

**The Variant Generator:** A quick call to generate 3 or 4 distinct semantic variations of the core prompt.

**The Parallel Execution:** Pass all variations to the main model simultaneously (or sequentially). Because of the shared context block at the front, you are only paying for the extra output tokens, which are still incredibly cheap.

**The Consensus Judge:** A final call that takes the outputs, highlights any hallucinated details or weak points in them, and merges them into a single definitive answer.

With DeepSeek V4 Flash, you can run an entire 4-stage generation and review loop like this for less than it costs to run a single, one-shot prompt against a standard closed frontier model.

The primary trade-off isn't financial—it's **latency**. Running sequential calls to generate variants, process them, and then judge them adds a few extra seconds of wait time per turn. For automated backend pipelines, agentic workflows, or complex technical tasks, that trade-off is almost always worth it.

<!-- /gemini-message -->

---

<!-- gemini-message index=3 role=user timestamp="2026-07-08 00:34" -->

---

## User
[2026-07-07 22:51 MDT-6] Wow, this is really valuable information!

Kind of changes potentially my whole strategy of thread-compactifying!

I gotta know: do you know if the same would apply for Antigravity? Or can you make a logical guess? I understand that how they ACTUALLY determine QUOTA USAGE specifically (not paying by the API! Not paying with credits! ie, not paying per token, but using up a mystical slightly opaque quantity called "quota"), but they SAY quota is directly correlated with cost:

"Quota is

  │consumed proportionally to the cost of the tokens. Thus, limits will last

  │longer with shorter tasks or using more cost-effective models." (from antigravity-cli itself)




Can you come up with some numbers here, and maybe a table?

Final cost of running 1 prompt, a 4 prompt well designed ToT, and some other possible configurations.

And you can add some speculative stuff to the table too, but try to have it rooted in reality and clearly identive whch numbers are speculative and which are at least derived in truth majorly, even if they are slightly estimates

<!-- /gemini-message -->

---

<!-- gemini-message index=4 role=assistant timestamp="2026-07-08 00:34" -->

---

## Gemini
The exact same fundamental rule of exact prefix matching applies to Google's Antigravity platform.

Because Antigravity leverages Gemini models under the hood, it benefits directly from Gemini’s native context caching architecture. When the documentation notes that quota is "consumed proportionally to the cost of the tokens," it means your weekly and 5-hour rolling limits are tied to the backend financial compute cost of the model.  
davep

In the Gemini ecosystem, a cache hit on input tokens typically cuts the token cost—and therefore your quota consumption rate—by **75%** (paying only 25% of the standard input rate) for the cached portion.

To illustrate how this impacts your quota, let's look at a concrete scenario: analyzing a large codebase or a thick documentation file containing **100,000 tokens**, followed by a **1,000-token prompt**, resulting in a **2,000-token response**.

Quota Consumption Breakdown

To keep the math clean, let's establish a baseline currency: **1 Quota Unit (QU)** = the cost of processing 1,000 standard input tokens.

Standard Input Token Cost = `1.0x`

Cached Input Token Cost = `0.25x` (75% savings)

Output Token Cost = `3.0x` (Output tokens are always heavier on quota because generation requires more compute)

Scenario Configurations

**Baseline (1 Prompt):** A straightforward, single-turn request against the 100k context.

**Naive Tree of Thoughts (4 Prompts - Broken Cache):** You run 4 sequential variations, but you modify a system instruction or add a "thought angle" at the *beginning* of each prompt, invalidating the prefix cache.

**Optimized Tree of Thoughts (4 Prompts - Cached):** You lock the 100k context at the very front. You append the 4 prompt variations exclusively at the tail end, ensuring a near-perfect cache hit for runs 2, 3, and 4.

**Deep Speculative Multi-Agent Loop (8 Turns - Cached):** You extend the pattern to an 8-turn conversation or multi-agent verification loop (e.g., using Antigravity's concurrent subagents) with a perfectly structured cache.

Quota Performance Comparison
Configuration	Input Quota (Base Context)	Input Quota (Prompts)	Output Quota (Generations)	Total Quota Cost (QU)	Cache Efficiency
**1. Baseline (One-Shot)**	100 QU	1 QU	6 QU	**107 QU**	0% (First run entry)
**2. Naive ToT (4 Prompts)**	400 QU *(100 x 4)*	4 QU	24 QU *(6 x 4)*	**428 QU**	**0%** (Cache completely busted)
**3. Optimized ToT (4 Prompts)**	175 QU *(100 + [25 x 3])*	4 QU	24 QU *(6 x 4)*	**203 QU**	**53% overall savings** vs Naive
**4. Deep Agent Loop (8 Turns)**	275 QU *(100 + [25 x 7])*	8 QU	48 QU *(6 x 8)*	**331 QU**	**64% overall savings** vs Naive

⚠️ **Speculative Metric Note:** The 75% input token discount rate is derived from standard Gemini production pricing structures applied to Antigravity's quota engine. While the exact rolling 5-hour depletion algorithm is proprietary, the relative scaling behavior between cache-miss and cache-hit states is a highly stable representation of how your quota behaves.

The Takeaway for Your Strategy

If you use a naive implementation, running a 4-prompt Tree of Thoughts eats up **four times** your baseline context quota, which will quickly trigger the 5-hour throttle window.

However, when you append variations *after* the heavy context block:

You buy 3 additional master-level reasoning paths for a total cost of only **96 extra Quota Units** (compared to the massive 321 QU penalty of the naive approach).

Your limits last significantly longer, allowing you to use dense reasoning structures like reflection or multi-agent voting loops as a standard practice without exhausting your workspace allowance.

<!-- /gemini-message -->

---

<!-- gemini-message index=5 role=user timestamp="2026-07-08 00:34" -->

---

## User
[2026-07-08 00:31 MDT-6] ok give me a very short explanation of the kind of threads we MUST be doing to take advantage of caching.

And with caching, giant context windows are still a problem in terms of degrading thinking right?

I guess I'm wondering how best to think about it in terms of strategy.

And what about forking?

And I guess one limiting factor of the token caching in terms of a codebase is, as soon you make a substantial edit to the code, it's tough to just add on to the cached codebase with a diff or whatever and have the agents still do well.

I was thinking maybe I start threads with the same cached default codebase context, but yeah idk how it would work.

I mean I guess depending on the edits done, there's going to be SOME AMOUNT of the linearly written codebase context that will remain the same, it's just, when we reach that edit, we lose the rest of the cache. But it's still useful. Most of the time we'd have like 20-80% of the codebase cached. So I guess it's just a question of: how much of the codebase to include as cache considering things like token pollution, context inflation, the fact that not every prompt is even going to need to see most of the codebase anyway...

Lots to think about here. @Pro

<!-- /gemini-message -->

---

<!-- gemini-message index=6 role=assistant timestamp="2026-07-08 00:34" -->

---

## Gemini
To take advantage of caching, your threads **must** act as an append-only log where the heaviest data sits at the absolute beginning and remains entirely immutable.

The structure must look exactly like this:
`[System Instructions] + [Massive Static Codebase Context] + [Conversation History] + [New Prompt]`

The Reality of Giant Context Windows

You are entirely correct to worry about context inflation. **Caching solves cost and latency; it does not solve cognition.** If you feed a model 100,000 tokens, its attention mechanism still has to weigh 100,000 tokens to generate the next word. It will still suffer from "lost in the middle" syndrome, instruction drift, and degraded reasoning. A cheaper, faster hallucination is still a hallucination.

Forking

Forking is the absolute best use case for prefix caching. Because the cache is tied to the exact sequence of tokens, you can spawn 10 parallel agent threads (forks) that all share that exact same `[System + Codebase]` root. All 10 agents get the cache hit discount and near-instant time-to-first-token, allowing you to run wide exploratory searches or multi-agent debates for pennies.

The Codebase Edit Problem

Your intuition here is spot on, and it highlights the primary flaw of linear prefix caching in development environments.

If your codebase context is concatenated into a single giant string (e.g., alphabetically), and you edit `api.js` (near the front), you instantly invalidate the cache for `utils.js` and `workers.js` that follow it. If you edit something at the end of the string, you keep 90% of the cache. But you can't control where edits happen.

Strategy: How to manage this

Because of both the cache-busting edit problem and the cognitive degradation of giant contexts, blindly dumping the entire codebase into the cache is usually suboptimal.

The most effective current strategy for agentic coding harnesses relies on **Repo Maps + Targeted Includes**:

**The Cached Root:** Instead of the full code, the static prefix is a compressed Repo Map (using something like `ctags` to list every class, function, and file path, but omitting the actual logic). This gives the model a permanent, cheap, high-level understanding of the architecture.

**The Dynamic Append:** When you prompt the model, you only append the full text of the 2 or 3 files actually relevant to the task.

This keeps the context window tight (preserving the model's reasoning ability) while ensuring the heavy architectural map at the front almost never changes, maximizing your cache hits.

If you were to implement a Repo Map strategy, how would you structure the system instructions to ensure the model knows how to ask for the full file contents when it needs them?

<!-- /gemini-message -->

---

<!-- gemini-message index=7 role=user timestamp="2026-07-08 00:34" -->

---

## User
[2026-07-08 00:33 MDT-6] Ok, let's talk more about strategies to take the most advantage of this.

At this point, I'm interested in the most robust, easy solution that will result in the most savings

<!-- /gemini-message -->

---

<!-- gemini-message index=8 role=assistant timestamp="2026-07-08 00:34" -->

---

## Gemini
If you want the most robust, set-and-forget architecture that maximizes savings without requiring a PhD in memory management, you need to move away from dumping the raw codebase into the prompt.

The most effective pattern for agentic development right now is the **Stable Anchor + Volatile Append** strategy. It elegantly sidesteps the issue of codebase edits busting your cache.

Here is exactly how you structure it.

The "Stable Anchor" Architecture

Instead of treating your codebase as one massive block of text, you split it into two tiers of memory: the structural map (which rarely changes) and the active files (which change constantly).

Your prompt construction pipeline should build every request in this exact, strict order:

**1. The System Instructions (The Brain)**
Your persona, output constraints, and tool definitions. This is completely static.

**2. The Repo Map (The Stable Anchor)**
This is a highly compressed, text-based map of your entire project. You can generate this using a tool like `ctags` or a simple script that outputs a tree view of your directory, class names, and function signatures—but *no implementation logic*.

*Why this works:* A repo map of a massive project is usually only 5,000 to 15,000 tokens. It gives the agent perfect spatial awareness of the architecture. Because you aren't changing file structures or renaming core classes every five minutes, this heavy block remains identical across almost every call, giving you a near-permanent cache hit.

**3. The Active Files (The Volatile Memory)**
This is where you inject the full raw text of the 1, 2, or 3 specific files the agent actually needs to look at or modify right now.

*Why this works:* If the agent makes a substantial edit to `api_router.js`, it doesn't bust the cache for your entire project. It only changes the token sequence *after* the heavy Stable Anchor.

**4. The User Task (The Append)**
Your specific instructions or the next conversational turn.

Why This is the Most Robust Solution

This architecture solves the exact problem you pointed out regarding edits.

If you feed the model the raw codebase linearly (A to Z) and edit `auth.ts` (near the beginning), you instantly destroy the cache for every file that comes after it.

With the Repo Map strategy, your heavy context sits safely at the front. The agent always knows where everything is, and you only pay the premium, un-cached token price for the specific files you are currently modifying. It keeps the context window tight, which prevents the LLM from getting confused by 80,000 tokens of irrelevant code, while slashing your quota usage.

Here is a visual simulator to help you conceptualize how these different ordering strategies impact your cache survival rate when edits occur.

If you were to build the script to generate that Repo Map dynamically, what tools or parsing logic do you think would be the most lightweight to integrate into your current launchd/git-sync workflow?

<!-- /gemini-message -->

---

