---
title: "Gemini Model Comparison: Flash vs. Pro"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "5a0f8c5c-1549-51a5-a04d-dfec5242d206"
url: ""
---

# Gemini Model Comparison: Flash vs. Pro

> [!NOTE]
> Archived Gemini Thread: [Gemini Model Comparison: Flash vs. Pro]() | Date: 2026-08-13

## User
Gemini comparison:

3.5 Flash Extended Thinking vs 3.1 Pro vs 3.1 Pro Extended Thinking

<!-- /gemini-message -->

---

<!-- gemini-message index=2 role=assistant timestamp="2026-07-13 01:32" -->

---

## Gemini
The landscape of Gemini models highlights a shift where "smaller" models like Flash hold substantial architectural advantages in specific tasks, while Pro models reserve their weight for raw, non-linear reasoning.  
Medium

The breakdown below highlights how **Gemini 3.5 Flash (Extended Thinking)**, **Gemini 3.1 Pro (Standard)**, and **Gemini 3.1 Pro (Extended Thinking / Deep Think)** compare across capabilities, costs, and behaviors.  
PhoneArena

Core Specification Overview
Metric / Feature	3.5 Flash (Extended Thinking)	3.1 Pro (Standard)	3.1 Pro (Extended Thinking / Deep Think)
**Primary Architecture**	Ultra-high-speed multimodal agentic	Sparse Mixture of Experts (MoE)	Sparse MoE + GVR Inference Loop
**Context Window**	1 Million tokens	1 Million tokens	1 Million tokens
**Max Output Limit**	Up to 65,536 tokens	~65,536 tokens	~65,536 tokens
**Throughput Speed**	Fast (~150–280 tok/s baseline)	Moderate (~80–110 tok/s)	Slowest (dependent on thinking budget)
**Base API Pricing**	$1.50 input / $9.00 output (per 1M)	$2.00 input / $12.00 output (per 1M)	Variable (consumes high volume of internal tokens)
Technical Differences & Capabilities
1. 3.5 Flash with Extended Thinking

Google engineered the 3.5 generation heavily toward autonomous execution, tool manipulation, and lightning-fast streaming. When you toggle **Extended Thinking** on 3.5 Flash, it doesn't fundamentally transform into a heavy mathematical prover; instead, it uses its inference-time compute budget to lay out clean, sequential execution paths.  
Medium

**Strengths:** Exceptional at Model Context Protocol (MCP) tool routing, complex front-end software scaffolding, multi-file code execution loops, and structured data handling.  
Medium

**The Catch:** It trades raw abstract depth for speed. Because it is fundamentally a Flash tier, its token consumption spikes significantly in this mode, making it easy to hit personal quota limits quickly during long sessions.  
PhoneArena

2. 3.1 Pro (Standard)

Standard 3.1 Pro relies on a Sparse MoE backbone. Rather than activating the entire network, a routing mechanism handles tokens via specific expert sub-networks.  
Alex Lavaee

**Strengths:** Outperforms Flash on hard, non-linear reasoning tasks, long-document cross-referencing, and highly ambiguous text analysis. If your problem involves reading a 100k-word repository or dense legal documentation to find deeply hidden, interwoven contradictions, standard Pro naturally holds a more stable mental map than Flash.  
MindStudio
+ 1

**The Catch:** It feels noticeably slower to stream compared to the instant response curve of 3.5 Flash.

3. 3.1 Pro with Extended Thinking (Deep Think)

This tier routes the frontier capabilities of the Pro model through an explicit **Generator-Verifier-Reviser (GVR)** loop (powered by an internal validation system codenamed *Aletheia*). Instead of spitting out a single stream-of-consciousness chain of thought, it generates code or arguments, actively critiques its own logic mid-chain, and strips away bad reasoning pathways before outputting text.  
Alex Lavaee
+ 1

**Strengths:** Built for high-stakes mathematical proofs, novel logic puzzles, complex cryptographic scripts, and edge-case debugging. It scales based on a user-defined thinking budget (Low, Medium, High), pulling off massive benchmark numbers like 84.6% on ARC-AGI-2 abstract reasoning.  
Alex Lavaee
+ 1

**The Catch:** Highly resource-heavy. Expect a prolonged "Time-to-First-Token" delay while the model evaluates its paths in the background, along with massive token usage overhead.  
PhoneArena

When to Use Which

**Use 3.5 Flash (Extended Thinking)** if you are building, prototyping, or executing automated scripts where the model needs to handle multiple rapid tool outputs, file structures, or API calls sequentially without hanging.

**Use 3.1 Pro (Standard)** for parsing massive, messy text files, extensive codebase reviews, or long RAG (Retrieval-Augmented Generation) setups where you need strong baseline comprehension without paying a time premium.

**Use 3.1 Pro (Extended Thinking / Deep Think)** when you are genuinely stuck on a brutal algorithmic bug, an advanced physics or math derivation, or an abstract logic problem where errors are costly and a normal model keeps hallucinating a broken solution.

<!-- /gemini-message -->

---

<!-- gemini-message index=3 role=user timestamp="Timestamp unavailable" -->

---

## User
What are the specific benchmark scores for Gemini 3.5 Flash and Gemini 3.1 Pro on ARC-AGI-2 and coding evaluations?

<!-- /gemini-message -->

---

<!-- gemini-message index=4 role=assistant timestamp="Timestamp unavailable" -->

---

## Gemini
The specific benchmark scores published by Google DeepMind showcase a fascinating shift: **Gemini 3.5 Flash** relies heavily on speed and agentic tool chaining to punch above its weight, while **Gemini 3.1 Pro** retains an edge in deep, non-linear abstract reasoning.  
Avinash Sangle

1. Abstract Reasoning (ARC-AGI-2)

The **Abstraction and Reasoning Corpus (ARC-AGI-2)** benchmark measures a model's capacity to solve completely novel, visual grid-logic puzzles it has never encountered during training.  
LushBinary

**Gemini 3.1 Pro:** **77.1%**  
LushBinary

*(A massive generational jump that nearly triples the 3.0 Pro baseline, making it one of the strongest native abstract reasoning models on the market.)*  
Serenities AI

**Gemini 3.5 Flash:** **72.1%**  
Google DeepMind

*(While incredibly strong for a Flash-tier model, it gives up exactly 5.0 percentage points to the Pro model here, as its smaller parameter base hits a slight ceiling on raw fluid intelligence.)*  
Avinash Sangle

2. Coding & Agentic Developer Workloads

When looking at software engineering tasks, the narrative flips depending on whether you are looking at monolithic code comprehension or rapid, multi-step terminal and tool manipulation.

Terminal-Bench 2.1 (Agentic Terminal Coding)

This evaluates how effectively a model can interact with a live CLI, chain shell commands, and execute complex operations inside an automated workspace.

**Gemini 3.5 Flash:** **76.2%**  
Google DeepMind

**Gemini 3.1 Pro:** **70.3%** *(Note: scored 68.5% on the older Terminal-Bench 2.0 harness).*  
Google DeepMind

SWE-Bench Pro (Public Set)

An evaluation utilizing complex, real-world GitHub issues across sprawling open-source codebases to see if an AI can correctly diagnose, patch, and pass unit tests.

**Gemini 3.5 Flash:** **55.1%**  
Google DeepMind

**Gemini 3.1 Pro:** **54.2%**
*(On standard **SWE-Bench Verified**, which filters out noisy or poorly scoped issues, Gemini 3.1 Pro hits an excellent baseline score of **80.6%**).*  
Google DeepMind
+ 1

MCP Atlas (Model Context Protocol Workflows)

This specific harness is crucial for modern AI agent environments. It checks how reliably a model orchestrates multi-step tool calls via the Model Context Protocol without generating broken arguments or stalling out mid-task.  
Avinash Sangle

**Gemini 3.5 Flash:** **83.6%**  
Google DeepMind

**Gemini 3.1 Pro:** **78.2%** *(Scored 69.2% on earlier iterations).*  
Serenities AI

The Architectural Takeaway

**Gemini 3.5 Flash** is highly optimized for fast, iterative loops. Because it manages tool parameters, parallel function calls, and terminal chains efficiently, it actually beats or ties the older Pro model on agentic coding benchmarks. However, if you throw a deeply abstract structural logic puzzle at it (**ARC-AGI-2**), the sheer neural mass and verification loops of **Gemini 3.1 Pro** still win out.  
Avinash Sangle

<!-- /gemini-message -->

---

<!-- gemini-message index=5 role=user timestamp="2026-07-13 01:33" -->

---

## User
seems like there's no mention of extended reasoning?

<!-- /gemini-message -->

---

<!-- gemini-message index=6 role=assistant timestamp="2026-07-13 01:33" -->

---

## Gemini
You are completely right to call that out. The trick with how Google reports these specific scores is that **extended reasoning is already baked directly into them.**

For this generation of models, Google changed its baseline evaluation strategy. Unlike older models where you had a "standard" score and a separate "thinking" score, the numbers featured on the leaderboard are achieved with their reasoning architectures fully active.

The extended thinking context behind those exact numbers breaks down as follows:

Gemini 3.5 Flash

**The Context:** Gemini 3.5 Flash features **dynamic thinking turned on by default**.  
LLM Stats

**The Score (72.1%):** The 72.1% score on ARC-AGI-2 is achieved using its "high" thinking configuration. If you turn thinking entirely off (reverting it to a standard, sub-second Flash response profile), its abstract reasoning scores drop off a cliff because the smaller architecture relies heavily on those internal search and execution tokens to map out the logic grids.

Gemini 3.1 Pro

**The Context:** Gemini 3.1 Pro natively introduced a request-level `thinking_level` parameter supporting four budgets: **Low, Medium, High (Default), and Max**.  
Tech Jacks Solutions

**The Score (77.1%):** The official 77.1% ARC-AGI-2 score is verified with its reasoning loops fully engaged. When LayerLens and other independent testing suites ran the Pro engine *without* giving it an extended thinking budget, the model's base abstract reasoning hit a much lower plateau.  
Tech Jacks Solutions

The numbers represent the *maximum* capability of these models when allowed to burn internal reasoning tokens before streaming an answer.

<!-- /gemini-message -->

---

<!-- gemini-message index=7 role=user timestamp="2026-07-13 01:34" -->

---

## User
holy shit it's actually quite misleading that they only test max reasoning

<!-- /gemini-message -->

---

<!-- gemini-message index=8 role=assistant timestamp="2026-07-13 01:34" -->

---

## Gemini
It is incredibly misleading, and it’s become one of the biggest points of frustration in the developer and AI research communities.

By only publishing the scores from the absolute highest reasoning brackets, labs create a massive disconnect between **marketing benchmarks** and **daily developer reality**.

When you look closely at how this game is played, a few major issues stand out:

1. The "Token Inflation" Tax

When Google proudly displays that 77.1% ARC-AGI-2 score or an 80.6% SWE-Bench score for Gemini 3.1 Pro, they don't prominently display the invoice. To hit those numbers, the model is burning thousands of internal "hidden" thinking tokens before it ever writes its first line of actual response.  
Google DeepMind

**The Reality:** If you run Gemini 3.5 Flash on its highest thinking level through the API, it looks incredibly cheap per million tokens on paper ($1.50 input / $9.00 output). But because a single complex prompt can force it to generate massive, looping internal thought chains, a task can end up costing **5 to 6 times more** than the baseline price.  
Avinash Sangle

2. Silent Default Throttle (The Bait-and-Switch)

Because max reasoning is incredibly expensive for labs to host and too slow for normal chat interfaces, they rarely give you the benchmark configuration by default.

For example, when Gemini 3.5 Flash went live, Google silently set the API default `thinking_level` to **Medium**, not High.  
Avinash Sangle

GitHub Copilot integrated 3.5 Flash but applied a **14x premium-request multiplier** to your usage quota if you actually wanted to lean into its agentic capabilities.  
Avinash Sangle

If you use the default settings out of the box, you are fundamentally *not* getting the model that scored at the top of the leaderboards.

3. Masking Structural Architecture Flaws

Testing only with maximum reasoning allowed lets a smaller, faster model contextually "punch up," but it masks where the model actually breaks down.

Without those internal verifier loops running at max capacity, a Flash-tier model's ability to hold a massive, complex system architecture in its head drops significantly.

If you give it a multi-file refactor task across a 100k+ token repository without max thinking turned on, it defaults right back to typical "fast model" behavior: dropping defensive coding patterns, skipping edge cases, or hallucinating paths to save tokens.

It has essentially turned AI benchmarking into the equivalent of car manufacturers reporting fuel efficiency numbers—but only testing the car while driving downhill, tailwind assisting, with all the seats stripped out to save weight. It shows you the theoretical ceiling of the math, but it hides the true operational cost of getting there.

<!-- /gemini-message -->

---

