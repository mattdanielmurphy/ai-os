# query_aios Cold-Start Recovery and Default Model

**Date:** 2026-09-22
**Context:** `scripts/query_aios.js` and the Perplexity engine in `apps/gemini-companion`

## Finding

The linked failed run found the companion server unreachable. `query_aios.js` issued `la restart ... || la start ...` with all output suppressed, then only waited 30 seconds. The launch agent was not loaded, so the caller received no actionable launch-agent error.

## Changes

- Use native launchd `enable`, `bootstrap`, and `kickstart` commands. This avoids the legacy `la load` path, which reported success despite the agent being disabled in launchd.
- Wait up to 90 seconds for cold startup; if still unavailable, make one additional kickstart attempt and wait another 90 seconds.
- Print native launchd status and `la logs` guidance on final failure.
- Set the CLI and planner default to GPT-6 Sol Thinking using Perplexity preference key `gpt6_sol_thinking`; preserve Terra as `--model terra`.

## Verification

- Confirmed the loaded launchd job, awake Perplexity and Gemini webviews, and healthy `/api/health` endpoint.
- Deliberately unloaded the launchd job and stopped its tmux child. The next `query_aios` invocation bootstrapped the plist, waited for readiness, and returned `AIOS_RECOVERY_OK` in 27.14 seconds using the default GPT-6 Sol Thinking route.
- Ran `node --check scripts/query_aios.js` and `git diff --check`.
