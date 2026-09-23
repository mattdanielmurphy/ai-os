# Perplexity Authentication Guard and Model Provenance

**Date:** 2026-09-22
**Scope:** `scripts/query_aios.js` and the Perplexity engine embedded by `apps/query-aios-companion`

## Finding

The CLI printed the requested model as if it were the model that generated the answer. Perplexity's current response parser and companion response contract do not provide verifiable model provenance. The engine also allowed requests with an empty session token, permitting guest behavior and a possible Sonar fallback.

## Changes

- Re-read the Perplexity page's session token for every query instead of trusting the engine's cached token.
- Stop before the request when no token is available, with instructions to sign in inside the AI-OS companion Perplexity window. The error explicitly says no prompt was sent.
- Report `Requested model` separately from `Actual model: unverified` and warn that Perplexity may use Sonar when the requested model is unavailable.
- Label the printed identifier as an AI-OS session ID; it is not a Perplexity account thread ID or permalink.
- Kept the requested model preference and aliases unchanged. No actual model is inferred from the request or an HTTP success response.

## Verification

- `node --check scripts/query_aios.js` passed.
- `cargo build --release --manifest-path apps/query-aios-companion/src-tauri/Cargo.toml` passed, with two pre-existing `objc` macro `cargo-clippy` cfg warnings and the existing `block` future-incompatibility warning.
- Restarted `aios-server`; `/api/health` reported online with the Perplexity window awake.
- `git diff --check` passed.
- No live query was sent to verify fallback behavior. The Perplexity response still does not expose actual-model provenance, so CLI output reports it as unverified.
