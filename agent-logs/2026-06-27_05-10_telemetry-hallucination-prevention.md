## Goal
Fix the Telemetry Hallucination issue where the agent guesses quota numbers.

## Changes Made
- Modified `/Users/matthewmurphy/projects/ai-os/scripts/get_last_cost.py` to add `***` at the end of the last line of the `[AGY TELEMETRY]` output block.
- Modified `/Users/matthewmurphy/.gemini/GEMINI.md` to update the telemetry rule, strictly forbidding manual typing or guessing of the telemetry block, and requiring the direct execution of the `get_last_cost.py` script.
- Updated `FEATURES.md` to document the Telemetry Hallucination Prevention changes.

## What Worked
- Precision modifications to `get_last_cost.py` and `GEMINI.md` using `precision_edit.py`.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- The cost script computes current turn and weekly/5h quota usage using sqlite and OpenRouter/Gemini API billing info, returning the telemetry output block directly.
