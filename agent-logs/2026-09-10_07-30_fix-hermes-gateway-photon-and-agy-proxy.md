# Agent Log: Fix Hermes Gateway Photon iMessage Connectivity & Agy Proxy Stream Bug

## Context & Problem
Matt reported that Hermes Gateway was failing when receiving inbound iMessages from Photon (`+1 (628) 264-7656`), returning:
`⚠️ The model provider failed after retries... vars() argument must have __dict__ attribute`.
Investigation revealed three interacting issues:
1. **Model & Provider Mismatch**: Hermes session had previously attempted to query `http://localhost:8082` (where LiteLLM was failing / Caddy TLS collided).
2. **Agy Proxy `UnboundLocalError`**: When routed to `agy-proxy` on port 8080 (`http://127.0.0.1:8080/v1`), streaming `agy` CLI output triggered `UnboundLocalError: cannot access local variable 'content' where it is not associated with a value` in `services/agy-proxy/proxy.py` on line 449 because `content` was evaluated outside the `if not streamed_response:` block. This error was caught by the proxy and appended to responses as `[Proxy Error]...`.
3. **Gateway Reconnection & Stale Session State**: The gateway was stuck in an `UPSTREAM_STREAM_DEGRADED` state from a prior network disconnect and retained a stale session entry.

## Changes Made
1. **Fixed `UnboundLocalError` in `services/agy-proxy/proxy.py`**:
   - Properly scoped the `if content:` check inside the `if not streamed_response:` block in `run_agy_stream()`.
   - Verified that `AIAgent` completion runs end-to-end cleanly against `gemini-3.6-flash-low` in 7.19s without any proxy error.
2. **Restarted Services & Verified Health**:
   - Restarted `agy-proxy` via `la restart agy-proxy`.
   - Restarted `hermes-gateway` via `la restart hermes-gateway`.
   - Verified the gateway pruned the stale failed session, connected to `api_server` (`127.0.0.1:8642`), connected to the Photon sidecar (`127.0.0.1:8789`), and established a live gRPC stream with `spectrum.photon.codes`.
