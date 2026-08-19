---
title: "Find litellm server port"
date: "2026-08-11"
conversation_id: "49d537412f9f"
source: "antigravity"
---

# Find litellm server port

## User

what's the litellm server port?

---

## Assistant

The LiteLLM proxy runs on **localhost:8082**.

---

## User

and the url for that is http://localhost:8082/v1?

---

## Assistant

Yes, the LiteLLM proxy OpenAI-compatible endpoint is at:

**http://localhost:8082/v1**

That's the standard pattern — LiteLLM exposes an OpenAI-compatible API at `/v1`, so client libraries (OpenAI SDK, etc.) point their `base_url` at `http://localhost:8082/v1`.

---
