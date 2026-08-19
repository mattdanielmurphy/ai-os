---
title: "Model Switch Clears Token Cache"
date: "2026-07-20"
conversation_id: "c01c1be5e65b1663"
source: "antigravity"
---

# Model Switch Clears Token Cache

## User

when you change models in the middle of a thread in agy or on gemini.google.com, do you lose the token cache from the thread?

---

## Assistant

Yes, **you lose the pre-computed token cache** for that specific conversation thread when you switch models mid-stream.

Here is exactly how it works under the hood:

1. The Cache is Model-Specific

Gemini uses a technique called **KV (Key-Value) caching** to store the processed mathematical representations of your conversation history. Because different models (e.g., Gemini 1.5 Flash vs. Gemini 1.5 Pro) have different internal architectures, hidden dimensions, and layer weights, a cache computed by one model is entirely gibberish to another.

The instant you swap the model dropdown:

The system cannot reuse the existing server-side cache.

On your next prompt, the entire thread history up to that point must be sent back to the newly selected model to be re-tokenized and re-processed from scratch.

2. The Practical Impact

**First Turn Latency:** Your very first prompt after switching models will take longer to respond because the new model is processing the entire thread history in one giant chunk.

**Cost (for API Users/AGY):** If you are using a pay-per-token interface (like an API workbench or AGY), that initial turn after the model switch will bill you for processing the full raw text input of the thread history.

Once the new model processes the thread for the first time, it will begin building a *new* token cache for subsequent prompts in that session.

3. Will you lose the chat history itself?

No. Your text history, code snippets, and uploaded context remain visible in the UI and will still be used as the context window for the new model. You only lose the *computationally cached state* (the performance shortcut), not the actual words spoken.  
Reddit

---
