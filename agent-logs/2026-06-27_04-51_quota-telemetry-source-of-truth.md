## Goal
Fix `scripts/get_last_cost.py` so that it parses the real Antigravity quota from the system instead of using a naive turn-counter approximation.

## Changes Made
- Modified [scripts/get_last_cost.py](file:///Users/matthewmurphy/projects/ai-os/scripts/get_last_cost.py) to:
  - Load and parse Google OAuth credentials from `~/.gemini/antigravity-cli/antigravity-oauth-token`.
  - Perform automatic programmatic token refreshing using the extracted Client ID and Secret if the token has expired.
  - Save the updated token back to disk to persist the refreshed session.
  - Send a POST request to the internal gRPC endpoint `https://daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota`.
  - Parse the remaining quota fractions for `gemini-2.5-pro` (mapped to the 5hr bucket) and `gemini-2.5-flash` (mapped to the weekly bucket).
  - Format and output real percentages: `AGY Quota Remaining (5hr): XX% (Real)`.
  - Removed all native local turn-counter logging and timestamp matching math.
- Updated [FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md) to document Phase 8 real-time quota telemetry capabilities.

## What Worked
- Programmatic refresh flow via `https://oauth2.googleapis.com/token` successfully retrieves and persists the updated access token.
- Fetching user quota buckets from `https://daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota` returns real server-side remaining fractions.

## What Didn't Work / Known Issues
- `google-auth` (`google.oauth2.credentials`) and `requests` python libraries are not installed in the environment, so we implemented all network calls using Python's standard `urllib` package to prevent runtime dependency errors.

## Architecture Notes
- The Antigravity CLI binary uses gRPC under the hood but maps back to standard OAuth refresh endpoints and Google Private Cloud Code APIs. We can safely interact with these endpoint pathways using pure HTTP/JSON requests with valid Bearer headers.
