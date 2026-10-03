# Perplexity Companion Auth Compatibility

**Date:** 2026-10-03 12:49 MDT  
**Scope:** `apps/gemini-companion/src-tauri/engines/perplexity-engine.js` and the production `query-aios-companion` debug probe

## Finding

The auth check in `/api/debug/ping` attempted to call `_getSessionToken` from outside the engine's IIFE. That function is private, so the probe reported `AUTH=false` even when the engine could access authentication state. Separately, the live signed-in Perplexity webview stored a current NextAuth session object under an account-scoped `pplx-next-auth-session` local-storage key, without any of the legacy `read_write_token` sources.

## Changes

- Exported a token-free auth diagnostic from `window.__aiosPerplexity` and changed the debug route to use it.
- Preserved legacy token discovery from page bootstrap objects and auth-shaped browser storage. Added current NextAuth session detection that requires a user object and a non-expired expiry timestamp; same-origin API requests already use `credentials: include` and can rely on the webview's session cookies.
- Recorded the compatibility behavior in `AG_CONTEXT.md` and the Perplexity payload reference wiki.

## Verification

- `node --check apps/gemini-companion/src-tauri/engines/perplexity-engine.js` passed.
- `cargo build --release -p query-aios-companion` passed. It emitted the existing two `objc` `cargo-clippy` cfg warnings and `block` future-incompatibility warning.
- Restarted the production `aios-server` launch agent with `la restart aios-server`.
- Live `/api/debug/ping` reported `PPLX=true | AUTH=true (next-auth-session) | TAURI=true | WEBKIT=true`; `/api/health` reported online with the Perplexity window active.
- A harmless live `query_aios.js` Perplexity request returned `4` in 1.73 seconds after the final rebuild. Model provenance remains unverified by Perplexity.
- `git diff --check` passed before the final documentation-only additions.
