---
title: "Identifying the AI Model"
date: "2026-08-09"
conversation_id: "20260809_173127_8625c1be"
source: "antigravity"
---

# Identifying the AI Model

## User

Who’s receiving this? Hermes? What model is configured to receive messages from here?

---

## Assistant

Hey! You're talking to **Hermes Agent** — the high-level reasoning engine for your local AI orchestration system.

The model configured for this session (via Photon/iMessage DM) is **deepseek/deepseek-v4-flash** on **OpenRouter**. That's what's driving this conversation right now.

You've also got `agy` running as a parallel worker-bee system on your machine with a LiteLLM proxy on port 8082 with tiered models.

What's up? Need something built, researched, or wrangled?

---

## User

What took so long for that response?

---

## Assistant

Fair question. A few things stacked up:

1. **Fresh session startup** — no prior context, so I loaded memory, user profile, skills, and environment context from scratch
2. **Model latency** — deepseek-v4-flash on OpenRouter isn't the snappiest model, especially for the first call in a session where it has to ingest all that system context
3. **Photon delivery** — messages route through iMessage which adds its own latency on top

First response in a fresh session is always the slowest — subsequent ones should be noticeably faster since everything's warm. How's it feeling now?

---

## User

Can you change settings to default Hermes model is agy: Gemini flash 3.6 low?

---

## Assistant

Let me check the Hermes config and figure out the right way to set this up

I can see the config. Currently `model.default` is `deepseek/deepseek-v4-flash` via OpenRouter. You want it to be `agy/gemini-3.6-flash-low` instead.

I see two ways to do this — let me check if `agy:flash-low` maps to the right model alias:

The aliases already have `agy-flash-low: agy/gemini-3.6-flash-low`. So I can set the default model to that alias.

Let me set

Done. `model.default` is now set to `agy/gemini-3.6-flash-low` (via the `agy-flash-low` alias).

Since you're in an active session though, this change won't take effect until you **start a new conversation** (`/new` or `/reset`). Current model stays until then.

That said — `agy/gemini-3.6-flash-low` still routes through the agy proxy on port 8080 which then calls LiteLLM on 8082 which calls Google. So there's an extra hop compared to running Gemini directly. Is that the intent, or do you want to test `google/gemini-3.6-flash` directly?

---

## User

That’s the intent! That way we use my antigravity quota instead of paying for api use.
Can you restart this conversation with Gemini 3.6 flash?

Uh oh

---
