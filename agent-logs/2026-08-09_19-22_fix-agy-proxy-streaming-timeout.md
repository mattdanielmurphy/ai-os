# Agent Log: Fixed agy-proxy Real-time Streaming & Timeout Bugs

**Date:** 2026-08-09 19:22  
**Author:** Antigravity  
**Files Modified:** `services/agy-proxy/proxy.py`, `~/.hermes/config.yaml`

## Problem
When using Hermes Agent configured with the custom `agy` provider (`http://127.0.0.1:8080/v1`), chat requests and tool turns would frequently freeze and terminate with `[Proxy Error]: timed out` after several minutes.

## Root Causes Identified
1. **Synchronous In-Memory Stream Buffering**: In `_proxy_to_litellm_stream()`, the proxy collected the entire LiteLLM SSE stream into a Python list (`all_lines = list(_stream_lines())`) inside a thread before yielding a single chunk to Hermes. This broke incremental token streaming completely (TTFT equal to total generation time).
2. **Blocking urllib Timeout**: The thread read loop used `urllib.request.urlopen(req, timeout=120)`. Any reasoning pause or generation exceeding 120s raised `socket.timeout: timed out`.
3. **Error Injection in Stream**: The caught exception was yielded as an assistant delta `[Proxy Error]: timed out` rather than an HTTP error, injecting raw error text directly into the agent's conversation history.
4. **Hermes Stale-Stream Watchdog Trigger**: Because 0 chunks were emitted while buffering, Hermes' client-side `_stream_stale_timeout` watchdog detected the stream as dead and killed the connection.
5. **Model Prefix & Name Inconsistencies**: Model names with prefixes (`@custom:agy:...`, `agy/...`) were passed unnormalized, and `~/.hermes/config.yaml` held deprecated aliases.

## Resolution
- Rewrote `_proxy_to_litellm_stream()` and `_proxy_to_litellm()` in `services/agy-proxy/proxy.py` using `httpx.AsyncClient` with zero-buffering async generator streaming (`aiter_lines()`).
- Enabled immediate, real-time chunk streaming with generous connection timeouts and no mid-stream read timeouts.
- Added `normalize_model_name()` to handle all alias expansions and prefix stripping (`@custom:agy:`, `agy/`, etc.).
- Dynamically populated `/v1/models` from LiteLLM and added `/v1/models/{model_id}` and `/health` probe endpoints.
- Updated `~/.hermes/config.yaml` with the full modern lean coding stack aliases.
- Restarted `agent-agy-proxy` service and verified streaming completions with tools. All 13 unit tests pass.
