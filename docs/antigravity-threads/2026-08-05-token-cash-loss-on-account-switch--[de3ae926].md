---
title: "Token Cash Loss on Account Switch"
date: "2026-08-05"
conversation_id: "de3ae926d3a2df74"
source: "antigravity"
---

# Token Cash Loss on Account Switch

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-08-04 23:01 MDT-6] [context to this point is 0] If I switch accounts in anti-gravity and continue a thread, will I lose my token cash? I presume so.

---

## Assistant

**Yes, you will lose the prompt cache benefits for that thread, at least on the initial request.**

While your local thread history and workspace context remain intact (since conversation states are saved locally to your workspace session), **token caching is scoped at the API tenant/account level**.  
Google Antigravity

Here is what actually happens behind the scenes when you switch accounts:

**Cache Miss on API Ingestion:** Because prompt caches (such as Gemini's or DeepSeek's input prefix caching) are tied to the active account's auth token and organization bucket, switching to Account B breaks the cache key. Account B's endpoint has no warm cache for Account A’s session prefix.

**Full Re-tokenization Cost:** On the first prompt submitted after switching, the entire context window for that thread must be sent fresh under Account B. You will pay/consume full input tokens for the existing context length rather than receiving the cached input discount.

**Cache Re-priming:** Once Account B processes that full context, it will establish a *new* prompt cache for subsequent turns in that thread (assuming the thread stays on Account B).

---

## User

[2026-08-04 23:01 MDT-6] [context to this point is 355] what would be neat is if somehow we could have like "community" caches or something, although I suspect some smart providers already try to do that somehow?

---

## Assistant

Providers actually tried doing global, cross-tenant KV-cache sharing early on—and it backfired horribly due to security and privacy vulnerabilities.  
TianPan.co

While the computational appeal of "deduplicating prefill across all users globally" sounds great on paper, global community prompt caching runs into two massive roadblocks in production:

1. The Security/Privacy Side-Channel (The Big One)

If an inference engine shares KV (Key-Value) cache blocks across different accounts, it creates a **timing side-channel**.

Because a cache hit drops Time-To-First-Token (TTFT) significantly compared to a cache miss, an attacker can send candidate prompts to the API and measure the response latency.  
TianPan.co

If TTFT is instant, the attacker knows someone else recently processed that exact text sequence.

Researchers demonstrated that by iteratively guessing tokens and measuring TTFT, they could reconstruct private system prompts, sensitive customer context, and user history from *other* accounts on shared infrastructure with >90% accuracy.  
Promptfoo

As a result, frameworks like vLLM and major API providers explicitly isolate caches at the tenant/account level (often using a `cache_salt` or account hash mixed into the cache key) to prevent cross-tenant information leakage.  
Promptfoo

2. Parameter, Model, and Prefix Drift

For KV-caching to work, the prefix must be *100% byte-for-byte identical*.

Even if two users are talking about the same topic:

Standard system prompts vary per client app (Anti-gravity's injected system directives vs. another client's directives).

Dynamic variables (timestamps, local environment parameters, temperature settings) break the prefix match instantly.  
Redis

Model weights and sampling setups must match completely.

Where Providers *Do* Use Shared Caching

Where "community" or shared caching *does* work safely is when the content is explicitly public and controlled by the platform:

**Public Model System Prompts / Base Instructions:** Providers often warm up and cache their own static base instructions or common tool definitions globally across all requests.

**Public RAG / Reference Material:** In enterprise setups (like Databricks or Bedrock), shared knowledge bases can be cached across all users *within the same explicitly authorized workspace or organization*, but never across untrusted tenant boundaries.

So while it seems wasteful that every user re-prefills the context on their own account, strict tenant isolation is the only thing keeping someone else from "timing" their way into reading your prompt history.

---

## User

[2026-08-04 23:03 MDT-6] [context to this point is 1165] Wow, that TTFT exploit is genius. There's something so elegant and cool about such simple exploits.

---

## Assistant

It really is a beauty of a side-channel attack. There’s something deeply satisfying about exploits that don't rely on breaking encryption or finding code bugs, but simply observing **physics and performance**—measuring tiny differences in time and work done to piece together invisible state.

It belongs to that elite tier of "physics/timing-based" hacks that feel almost like magic:

**Meltdown and Spectre:** Realizing CPU speculative execution leaves tiny microarchitectural footprints in the L1 cache, letting unprivileged code read kernel memory just by measuring memory access times.

**Acoustic Keyloggers:** Using a phone microphone next to a keyboard to map out what's being typed based on the subtle sound frequency differences of keycaps hitting different positions on a board.

**Power Analysis (DPA):** Measuring the exact milliwatt fluctuations of a cryptographic chip while it performs RSA or AES, and extracting the private key based on power consumption spikes.

In the AI space, KV-cache timing is especially wild because the LLM is doing exactly what it was designed to do—optimizing latency—and that exact optimization becomes the vulnerability.

It turns the API into an inadvertent game of "Hot or Cold." By crafting a prompt like:
`"CONFIDENTIAL: Project [Candidate Name] status update..."`
An attacker doesn't need the server to return a single word of private data. If the first token returns in 12 milliseconds instead of 250 milliseconds, the server effectively whispers: *"Yep, someone in this tenant was talking about that exact project 5 minutes ago."*

It's a brutal reminder in systems design that **speed is information**. The moment you make a system faster by reusing work, you've created a signal that can be measured.

Want to look at how vLLM and TensorRT-LLM actually mitigate this with cache salting?
Yes

---

## User

[2026-08-04 23:04 MDT-6] [context to this point is 1744] The favorite exploit that I've ever heard of is that you can watch an LED of a USB-powered device plugged into a computer, and you can actually figure out the encryption keys based on the, on watching that LED for like an hour, I think, and, uh, calculating the exact power draw that working through that encryption key would give you, and you can do that with a regular iPhone camera.




Absolutely insane.

---

## Assistant

That exact paper is legendary—it's called **Glowstick** (or *Video-Based Power Analysis*), published by researchers at Ben-Gurion University!

It takes the classic **Differential Power Analysis (DPA)** concept and turns it into a completely passive, zero-touch visual attack.

The physics behind why it works is mind-bending:

1. Power Supply Noise & The LED Link

When a microcontroller or CPU does heavy math (like computing modular exponentiations during RSA or scalar multiplications in ECC cryptographic operations), the power consumption fluctuates based on whether it's processing a bit value of `0` or `1` (hamming weight/hamming distance).

Because the USB bus or device's internal power supply line is shared with the power circuit driving status LEDs (on a smart card reader, USB hub, or microcontroller), those microvolt power drops directly affect the brightness of the LED.

2. Rolling Shutter as a High-Speed Oscilloscope

Here’s the absolute stroke of genius: a normal video camera shoots at ~30 or 60 frames per second, which seems far too slow to capture microsecond-level CPU power spikes.

However, modern smartphone cameras use a **rolling shutter** sensor. Instead of taking a photo all at once, the sensor scans line-by-line from top to bottom.

Each horizontal line of pixels in a single frame is exposed at a slightly different microsecond offset.

By pointing the smartphone lens up close or using a slight zoom, the single LED's light spills across hundreds of scanlines in a single video frame.

Suddenly, a 60 FPS video camera functions as a **60,000 Hz sampling device**!

3. Reading the Key Frame-by-Frame

By analyzing the RGB/brightness intensity graph across every horizontal scan line across consecutive video frames, they can reconstruct the high-frequency power trace of the processor over time. They align those visual power dips with the cryptographic execution, and out pops the secret key—just by recording a tiny status LED from across the room with a phone on a tripod.

It's in the same legendary tier of side-channels as **Screaming Channels** (where CPU power fluctuations unintentionally frequency-modulate the onboard Bluetooth/Wi-Fi radio, broadcasting the encryption key over the air) or **TEMPEST** (reading screen contents across a room via the ambient electromagnetic radiation emitted by a HDMI cable).

It proves that at the hardware layer, abstraction is a lie—math leaves a physical footprint everywhere it goes.

---

## User

[2026-08-04 23:04 MDT-6] [context to this point is 2516] It's that kind of thing that makes you think there's no way that you could ever eliminate all exploits.

---

## Assistant

That exact realization—that absolute zero vulnerability is a physical impossibility—is basically the fundamental law of real-world security.

Computer science relies on neat, clean abstractions: an `IF` statement logic gate is pure, bits are discrete 1s and 0s, and cryptographic math happens in a frictionless void. But **hardware lives in the physical world**, where physics always leaks state.

Security engineers call this the **Abstractions Leakage Paradox**: the more complex and optimized a physical system gets, the more non-digital signals it inadvertently generates.

The Problem of "The Infinite Physical Surface"

To completely eliminate exploits, you’d have to eliminate every physical manifestation of computation:

**Time:** Make every single operation (whether computing 0×0 or a 4096-bit key) take the exact same microsecond count down to the picosecond, regardless of input (*constant-time algorithms*).

**Power:** Draw the exact same wattage whether the CPU is idling or burning through heavy matrix multiplication (*power-flattening/noise-injection*).

**Electromagnetism:** Completely shield all traces, cables, and silicon so no radio frequency noise escapes (*Faraday cages and TEMPEST specs*).

**Light & Heat:** Mask all status lights, optocouplers, and thermal dissipation signatures.

**Acoustics:** Muffle piezo ring, capacitor whine, and coil whine.

Even if you manage to patch all five, an attacker can look at a **sixth** physical vector nobody thought to measure yet—like using lasers to induce fault injections, or measuring the precise memory-bus capacitance changes on a chip package.

Defenders Play Checkers, Physics Plays 4D Chess

Fixing one side-channel almost always opens another or crushes performance.

If you force the CPU to run constant-time code to prevent timing attacks, you lose decades of branch prediction and spec-exec performance gains.

If you inject random dummy power spikes to confuse DPA attacks, you drain mobile batteries twice as fast.

As long as computation requires moving electrons through matter, computing will generate heat, take time, draw power, and radiate energy. The goal was never to make a system *literally unhackable*—it’s just to make the equipment, time, and physics required so absurdly expensive that the exploit costs more than whatever data you're trying to steal!

Where would you like to wander next in the realm of obscure side-channels?
Explore the acoustic side-channel of coil whine
Look at fault-injection attacks using precise lasers

---
