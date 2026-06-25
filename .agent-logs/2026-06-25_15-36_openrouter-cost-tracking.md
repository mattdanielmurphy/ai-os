## Goal
Build a cost-tracking protocol for the AI OS workspace — a lightweight script that fetches per-message OpenRouter billing data, plus a mandatory post-response instruction in AG_CONTEXT.md forcing Claude to display the cost after every turn.

## Changes Made
- **`scripts/get_last_cost.py`** — New file. Python delta-tracking script that queries OpenRouter's `/api/v1/credits` endpoint, stores the last-known total usage in `.last_usage`, and reports the cost of the single exchange since the previous invocation. Uses only stdlib (urllib, json). Gracefully handles missing API key, network errors, and usage resets.
- **`AG_CONTEXT.md`** — Added "Mandatory Post-Response Protocol" section (§20–27) with an absolute-path invocation command, plus a durable knowledge entry for 2026-06-25 documenting the protocol.

## What Worked
- The delta-tracking approach works perfectly: first call seeds the baseline, second and subsequent calls report the exact cost of the last exchange (confirmed: $0.005342 for the test invocation).
- No external pip dependencies needed.
- The `/credits` endpoint works with a standard API key (no management key required, unlike `/activity`).

## What Didn't Work / Known Issues
- OpenRouter's `/api/v1/activity` endpoint returns 403 for non-management keys — can't use it to surface per-generation token counts or provider info. Consider upgrading to a management key if token-level detail is needed later.
- The delta approach cannot attribute cost to individual messages within the same agent turn.

## Architecture Notes
- OpenRouter API: `/credits` returns `total_usage` and `total_credits`; `/activity` with `limit=N` returns per-generation metadata but requires a management key.
- State file `.last_usage` lives alongside the script, in `.gitignore`-friendly territory.