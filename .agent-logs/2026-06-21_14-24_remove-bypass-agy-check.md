## Goal
The user requested two things:
1. Remove the `BYPASS_AGY` environment variable check, which was incorrectly bypassing the `agy` CLI agent when set.
2. Investigate and fix why the CLI tool takes an inordinate amount of time to answer simple questions.

## Changes Made
- Modified `src/index.js` to remove the `process.env.BYPASS_AGY === 'true'` conditional branch.
- Removed the slow `ptySession.executeCommand('/Users/matthewmurphy/.local/bin/agy --dangerously-skip-permissions --print "echo test_health"', 15000)` pre-flight check. This check was executing a full LLM inference step *before every task* just to see if the CLI was healthy, which added ~10-15 seconds of overhead to every query. It was replaced with a direct boolean assignment, relying on the pre-existing fast `checkAgyHealth()` settings validation.

## What Worked
- Removing the LLM-based pre-flight check significantly speeds up the initial routing/execution time, answering the user's performance complaint.
- Removing `BYPASS_AGY` satisfies the instruction to get rid of that env var check.

## What Didn't Work / Known Issues
- None so far. The CLI now cleanly skips the artificial wait time and properly delegates straight to `agy` or Direct API based on configured limits and runtime behavior rather than an expensive startup check.

## Architecture Notes
- `checkAgyHealth()` checks `~/.gemini/antigravity-cli/settings.json` natively, which is an immediate JSON parse.
- Previously, the CLI did a redundant LLM inference check to verify health, completely neglecting the fact that `agy` already captures quota errors during regular task execution if the LLM fails. By omitting the pre-flight ping, we avoid a full model invocation cycle, optimizing the system's "Time-To-First-Action".
