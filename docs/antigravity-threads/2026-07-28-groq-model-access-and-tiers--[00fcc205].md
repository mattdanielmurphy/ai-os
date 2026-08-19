---
title: "Groq Model Access and Tiers"
date: "2026-07-28"
conversation_id: "00fcc20556a63ab3"
source: "antigravity"
---

# Groq Model Access and Tiers

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Note-Taking Directive: When asked to "make a note about this" OR if we discuss anything interesting or ideas about future projects, you MUST proactively output a JSON tool call to save it as a note, or update an existing note. The JSON must be inside a ```tool_call codeblock. Schema: {"tool":"save_note","args":{"title":"Note Title","content":"Markdown content...","update":false}}. The userscript will execute this automatically and save it to Development/Project Notes/.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




I think I remember hearing that groq has like accelerated models somehow, at slightly extra cost?

Can I get a fast deepseekv4 flash for slightly more than regular?

---

## Assistant

Groq doesn't actually offer an "accelerated/boosted" paid tier for individual models like DeepSeek V4 Flash.  
eesel AI

Here is what is likely triggering that memory and how the platform actually works:

1. How Groq's Tiering Actually Works

Groq's entire platform is built around its custom LPU hardware, so *all* inference is already running at full hardware acceleration by default (often hitting 300 to 800+ tokens/second).  
AI Pricing Guru

Instead of an "accelerated model tier," Groq splits its API into usage tiers:

**Developer (Free Tier):** Generous rate limits (RPM/TPM caps), but strictly subject to queueing and rate-limiting during high traffic.  
AI Pricing Guru

**Pay-As-You-Go (Standard Paid Tier):** Billed per 1M tokens with no monthly minimum. Moving from Free to Paid doesn't give you a faster model, but it unlocks higher Rate Limits (TPM/RPM) and bypasses free-tier throttling.  
AI Pricing Guru
+ 1

**Provisioned Throughput (Enterprise):** You pay for dedicated, reserved LPU capacity (guaranteed tokens/sec) so your throughput never drops during peak global load. This is where people spend "slightly extra" (or a fixed baseline fee) to guarantee instant, unthrottled burst speeds.

2. DeepSeek V4 Flash Details

If you want to run `deepseek-v4-flash`, Groq isn't the only option, and the pricing structure across options breaks down as follows:  
AI Pricing Guru

**First-Party / Direct API (DeepSeek):** Billed at roughly **$0.14 / 1M input** and **$0.28 / 1M output**. Extremely cheap, but direct API endpoints can occasionally hit rate-limit congestion during peak hours.  
AI Pricing Guru

**Third-Party Inference Hosts (Groq, Fireworks, Together AI):** Billed slightly above direct rates, but you get higher raw token output speeds (TPS) and more reliable infrastructure.  
AI Pricing Guru

If you're looking for ultra-fast V4 Flash execution, paid Pay-As-You-Go access on Groq or Fireworks yields standard high-speed inference without requiring specialized "accelerated" model variants.

---

## User

I use openrouter.

But I like the idea of using deepseek v4 flash with higher TPS if it's not massively more expensive

---

## Assistant

Here is the best part: **you don't need to leave OpenRouter or pay a steep premium to get maximum throughput for DeepSeek V4 Flash.**

Because OpenRouter is an aggregator, it routes `deepseek/deepseek-v4-flash` across ~20 different hosting providers (e.g., Fireworks, DeepInfra, Together, etc.). Standard baseline pricing sits around **$0.09–$0.14 / 1M input** and **$0.18–$0.28 / 1M output**, which is insanely cheap.

To force OpenRouter to route your requests specifically to the highest TPS (tokens per second) providers, use OpenRouter's built-in routing mechanisms:

How to Force High TPS on OpenRouter
Option 1: Append `:nitro` to the Model Name

OpenRouter supports model flags. Appending `:nitro` forces the router to prioritize maximum throughput and minimal latency over absolute lowest cost:

JSON

```
{
  "model": "deepseek/deepseek-v4-flash:nitro"
}

```

Option 2: Define Provider Preferences in the Payload

If you want fine-grained control over how OpenRouter handles speed vs. cost, pass a `provider` object in your request:

JSON

```
{
  "model": "deepseek/deepseek-v4-flash",
  "provider": {
    "sort": "throughput",
    "allow_fallbacks": true
  }
}

```

Does it cost "massively more"?

**No.** Flash models have a tiny active parameter footprint (~13B active), meaning even high-speed hardware hosts charge practically nominal rates.

Sorting by throughput might shift your price by a fraction of a cent per million tokens compared to the absolute rock-bottom provider on the list. You get 200–400+ TPS speeds without any noticeable jump on your bill.

---

## User

what would be nice is if I could set like an upper bound in price as say: choose the fastest option unless it's > $x

---

## Assistant

OpenRouter actually supports this exact feature directly in the payload!

You can pair `sort: "throughput"` (or `sort: "latency"`) with the `max_price` parameter inside the `provider` object. OpenRouter will rank all available hosts by speed and automatically drop any provider whose pricing exceeds your threshold.

The Payload Structure

Set your max USD price per million tokens (for prompt and completion) alongside your sorting preference:

JSON

```
{
  "model": "deepseek/deepseek-v4-flash",
  "provider": {
    "sort": "throughput",
    "max_price": {
      "prompt": "0.20",
      "completion": "0.40"
    },
    "allow_fallbacks": true
  }
}

```

How it operates under the hood:

**Filters:** OpenRouter looks at all active providers for `deepseek/deepseek-v4-flash` and immediately ignores any provider charging more than $0.20/1M input or $0.40/1M output.

**Sorts:** Among the remaining "cheap enough" providers, it selects the one with the highest real-time tokens per second (throughput).

**Falls back:** If the fastest qualified provider goes down or gets rate-limited, it automatically falls back to the next fastest provider that still respects your `max_price` cap.

---

## User

ok but even the fastest provider (Deepseek itself) on openrouter is 83 tps. I've gotten used to 3.6 flash which is crazy fast. It doesn't have to be that fast but... what about services like groq etc?

---

## Assistant

The ~80 TPS cap on DeepSeek V4 Flash comes down to **hardware architecture**. Most OpenRouter hosts run DeepSeek models on standard GPU clusters (Nvidia H100s/A100s), where memory bandwidth bottlenecks max output speeds around 30 to 100 TPS.

If you want the 300 to 1,000+ TPS streaming speed you're used to on Flash, you need providers running on **custom silicon** or **speculative decoding engines**.

Custom-Silicon Alternatives & Speeds

Hardware-accelerated inference platforms don't host every model—they carefully compile specific open-weights models for custom chips:

Provider	Hardware / Tech	Speed Range	Best Supported Models
**Cerebras**	Wafer-Scale Engine (WSE-3)	**1,500 – 3,000+ TPS**	Llama 3.1 8B / 70B
**Groq**	LPU (Language Processing Unit)	**300 – 800+ TPS**	Llama 3.3 70B, Qwen 27B
**SambaNova**	RDU Dataflow Chips	**400 – 600+ TPS**	Llama 3.3 70B, MiniMax
**Fireworks AI**	Speculative Decoding	**200 – 400 TPS**	DeepSeek R1/V3 distilled, Llama 70B
How to Get Custom Silicon Speeds on OpenRouter

You don't need a separate Groq or Cerebras account—**OpenRouter routes to these custom providers directly.**

If you want ultra-fast responses similar to Gemini Flash, swap the target model in your OpenRouter request to one hosted on dedicated silicon:

**For Maximum Raw Speed (1,000+ TPS):**

Target `meta-llama/llama-3.1-8b-instruct` or `meta-llama/llama-3.3-70b-instruct`.

Set your provider parameter to prioritize Cerebras or Groq:

JSON

```
{
  "model": "meta-llama/llama-3.3-70b-instruct",
  "provider": {
    "order": ["Cerebras", "Groq"],
    "allow_fallbacks": true
  }
}

```


**For Coding & Complex Reasoning at High Speed:**

Target Qwen or Llama 70B on Groq or SambaNova. They hit 300–500 TPS while maintaining top-tier instruction following and code generation.

Cost Impact

Custom silicon inference is surprisingly cheap because high token throughput reduces the active compute duration per request. Llama 3.3 70B on Groq or Cerebras typically runs between **$0.10 and $0.60 per 1M tokens**—costing essentially pennies while delivering instantaneous responses.

---

## User

you're not really getting it.

I'm talking like 200-300tps but as smart as deepseek v4 flash with med reasoning say

---

## Assistant

That's fair—let's skip the general speed tier conversation and focus directly on that exact sweet spot: **200–300+ TPS output speeds paired with high/medium reasoning capabilities.**

Here is the exact state of what exists for that specific combination right now and why standard OpenRouter setups hit a wall.

Why DeepSeek V4 Flash Caps at ~80–100 TPS

Even though `deepseek-v4-flash` has a light active parameter count (around 13B active), its large MoE architecture and total memory footprint mean almost every provider (DeepInfra, Baseten, Novita) hosts it on standard H100/B200 GPU clusters running standard vLLM or SGLang engines. On standard GPU clusters, memory bandwidth physically limits single-stream auto-regressive generation to **~70–120 TPS**.

To get **200–300+ TPS** at DeepSeek V4 Flash reasoning levels, you have to look at providers using **Speculative Decoding** or **Custom Silicon** on models in the same intelligence class.

Where to Get 200–300+ TPS at V4 Flash Intelligence
1. Fireworks AI (Speculative Decoding Engine)

**Speed:** **200 – 400 TPS**

**Intelligence Class:** Matches/exceeds DeepSeek V4 Flash medium reasoning.

**Key Models:** `qwen/qwen-2.5-72b-instruct` or `fireworks/qwen-3-72b` with speculative decoding enabled.

**Why it works:** Fireworks runs FireAttention and adaptive speculative draft models, allowing larger 70B+ class reasoning models to output at 3x normal GPU speeds. You can call this directly or route to Fireworks via OpenRouter (`fireworks` provider target).

2. SambaNova (RDU Dataflow Chips)

**Speed:** **400 – 600 TPS**

**Intelligence Class:** High reasoning / agentic capabilities.

**Key Models:** `minimax/minimax-m2` or `meta-llama/llama-3.3-70b-instruct`.

**Why it works:** SambaNova’s Dataflow architecture completely bypasses standard H100 memory bandwidth bottlenecks. It outputs dense 70B-class models faster than standard GPUs can run 8B models.

3. Groq (LPU Acceleration)

**Speed:** **300 – 500 TPS**

**Intelligence Class:** Strong instruction following & reasoning.

**Key Models:** `meta-llama/llama-3.3-70b-instruct` or `qwen-2.5-coder-32b`.

**Why it works:** Groq's LPUs execute reasoning models without token stutter. While Groq doesn't host direct DeepSeek V4 weights, Llama 3.3 70B or Qwen 32B Coder on Groq gives you that exact ~300 TPS streaming speed with reasoning on par with V4 Flash for code and logic.

Real-World OpenRouter Routing Strategy

If you want to stay inside OpenRouter and hit that 200–300 TPS threshold with V4 Flash-level intelligence, target a 70B or Qwen reasoning model explicitly routed to **Fireworks**, **SambaNova**, or **Groq**:

JSON

```
{
  "model": "meta-llama/llama-3.3-70b-instruct",
  "provider": {
    "order": ["Fireworks", "SambaNova", "Groq"],
    "allow_fallbacks": true
  }
}

```


This setup gets you right into the 200–400 TPS band with reasoning capabilities equal to or stronger than DeepSeek V4 Flash, without paying enterprise minimums.

---

## User

so there's no accelerated version of deepseek v4 flash?

I want it soecifically because deepseek is crazy cheap for what it is

---

## Assistant

Short answer: **no, there is no hyper-accelerated LPU/custom-chip version of DeepSeek V4 Flash.**

If you want V4 Flash specifically because of its ultra-cheap pricing (~$0.09 / $0.18 per 1M tokens), **80 to 120 TPS is currently the hard ceiling** across all hosting providers.

Why an "accelerated" version doesn't exist for V4 Flash

**Hardware Host Compatibility:** LPU/Wafer providers like Groq, Cerebras, and SambaNova don't automatically host every new open-weight model. Compiling a 284B total parameter MoE model (even with a 13B active footprint) onto custom ASIC/LPU chips requires custom kernel engineering.

**Current Hosting Infrastructure:** Every provider on OpenRouter serving DeepSeek V4 Flash (DeepInfra, Fireworks, Novita, SiliconFlow, etc.) is running it on standard Nvidia GPU clusters (H100s/A100s/B200s). On standard GPU architecture, memory bandwidth limits auto-regressive generation for this model size to roughly ~80–120 TPS.

How to squeeze the max speed out of V4 Flash on OpenRouter

While you can't hit 300+ TPS on V4 Flash today, you can make sure you're getting the top of its range (100–120 TPS with fast time-to-first-token):

**Force Fireworks or DeepInfra:** In OpenRouter, target Fireworks or DeepInfra via provider preferences. They run tuned vLLM/FireAttention stacks that push V4 Flash to its practical upper limit (~100–120 TPS) rather than the slower ~30–50 TPS providers.

**Set your payload:**

JSON

```
{
  "model": "deepseek/deepseek-v4-flash",
  "provider": {
    "order": ["Fireworks", "DeepInfra"],
    "allow_fallbacks": true
  }
}

```


Unless Groq or SambaNova explicitly add V4 Flash to their hardware compilations down the road, you're looking at a hard trade-off: **stick with DeepSeek V4 Flash at ~100 TPS for rock-bottom prices**, or switch to **Llama 3.3 70B on Groq/Cerebras at 300–1,000+ TPS** for a slight price step up.

---
