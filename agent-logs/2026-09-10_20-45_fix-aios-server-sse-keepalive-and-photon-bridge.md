# Agent Work Log: Fix AI-OS Companion Server SSE Keepalive & Photon Bridge

- **Date**: 2026-09-10 20:45 MDT
- **Context**: Photon iMessage bridge failed to respond to incoming messages ("221 Westbrook Wynd, Fort Saskatchewan. Save that to your global memory" and "Hello?").

## Root Cause Analysis
1. **Streaming Idle Read Drop**: When `hermes-gateway` queried `http://127.0.0.1:3031/v1/chat/completions` with `stream: true`, the Axum handler in `apps/gemini-companion/src-tauri/src/server.rs` emitted HTTP 200 SSE headers immediately but produced zero bytes while waiting for WebKit / Perplexity generation (which took ~29.2s). Hermes's `httpx` HTTP client encountered an idle read timeout at 29.21s and dropped the connection.
2. **Hyper TCP Reset on Body Stream Error**: The existing `server.rs` code returned `std::io::Error` on the streaming channel when an error occurred, which caused Hyper to abruptly drop the TCP connection rather than cleanly terminating chunked transfer encoding (`RemoteProtocolError: peer closed connection without sending complete message body`).
3. **Host Network Route Drop**: Simultaneous to the streaming timeout, the host experienced a network failure (`ENETUNREACH` to `spectrum.photon.codes:443`), causing the Photon sidecar `/send` to fail with HTTP 500 (`UPSTREAM_STREAM_DEGRADED`). The sidecar remained offline until 20:09 MDT, causing subsequent messages like "Hello?" to not reach the gateway.

## Resolution
1. **SSE Heartbeat Keepalive**: Added a 3-second periodic SSE comment ping (`: keepalive\n\n`) to `handle_openai_chat` in `apps/gemini-companion/src-tauri/src/server.rs`. Clients and proxies (such as `httpx` or LiteLLM) now maintain an active read socket regardless of long thinking or model delays.
2. **Graceful Error Frame Emission**: Replaced raw `io::Error` body termination with a structured OpenAI chunk (`⚠️ [AI-OS Error]: <msg>`) followed by `data: [DONE]\n\n`, preventing Hyper TCP RSTs and protocol errors.
3. **Rebuilt & Supervised `aios-server`**: Rebuilt the Tauri companion app, resolved Rust type annotations for `unfold`, and verified stream keepalive via `curl -N http://127.0.0.1:3031/v1/chat/completions`.
4. **Restarted `hermes-gateway`**: Restarted `hermes-gateway` via `la restart hermes-gateway`. Reconnected to Photon sidecar on 127.0.0.1:8789, redelivered pending obligations, and confirmed healthy dual-platform operation.
5. **Fulfilled User Requests**:
   - Geocoded parents' address (`221 Westbrook Wynd, Fort Saskatchewan` -> Lat: `53.6734896`, Lon: `-113.2540901`).
   - Created geofenced Apple Reminder: `apple-reminders add --title "Print off UPS return label for aerator" --location-name "Parents' House (221 Westbrook Wynd, Fort Saskatchewan)" --lat 53.6734896 --lon -113.2540901 --proximity enter`.
   - Persisted address to Mem0 (`aios-memory add ...`) and `~/.hermes/memories/MEMORY.md`.
