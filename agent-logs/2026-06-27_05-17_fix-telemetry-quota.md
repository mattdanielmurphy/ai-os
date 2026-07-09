## Goal
Fix the telemetry script's fake data fallback to accurately reflect local database tracking for AGY quotas, and update the global rule to print/copy telemetry output in the UI.

## Changes Made
- Modified `/Users/matthewmurphy/projects/ai-os/scripts/get_last_cost.py` to:
  - Track if API quota fetching succeeded (`is_real`).
  - Calculate remaining 5-hr and weekly quotas from local database turnovers (`agy_turns` timestamps in `~/.ai-os-telemetry.json`) if the API cannot be fetched.
  - Omit the ` (Real)` suffix in output when using the local database fallback.
- Modified `/Users/matthewmurphy/.gemini/GEMINI.md` to update the `TELEMETRY RULE` instructing the agent to run the script and copy the exact output to the bottom of the response.

## What Worked
- Falling back to local database statistics calculates 5-hr and weekly quota values accurately using `agy_turns` logs when API is unavailable.
- Updated `GEMINI.md` successfully.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Quotas are locally calculated as `(LIMIT - current_turns) / LIMIT`.
- `LIMIT_5H` is 50.
- `LIMIT_WEEK` is 200.
