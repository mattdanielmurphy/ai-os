## Goal
Remove the hardcoded fake/fallback quota approximation lines from the telemetry reporter script.

## Changes Made
- Modified `/Users/matthewmurphy/projects/ai-os/scripts/get_last_cost.py` to:
  - Remove unused constants `LIMIT_5H` and `LIMIT_WEEK`.
  - Remove `get_local_quotas()` which computed fake turn-count-based quota estimates.
  - Modify the output block to print `N/A` for quota lines if the real Antigravity quota endpoint cannot be reached or fails, instead of falling back to fake turn-counter approximations.

## What Worked
- Script successfully fetches and prints actual server-side percentages when available, and gracefully outputs `N/A` when the API call fails or is unavailable without falling back to fake data estimates.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The quota telemetry now relies purely on `get_antigravity_quota()` via direct OAuth token checks and retrieving the `remainingFraction` values from `daily-cloudcode-pa.googleapis.com`.
