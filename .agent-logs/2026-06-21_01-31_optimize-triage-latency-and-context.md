## Goal
Address latency issues and context blindness in the local Node.js gateway by upgrading the executive triage and command execution structures.

## Changes Made
- Modified [src/index.js](file:///Users/matthewmurphy/projects/ai-os/src/index.js):
  - Defined `DEFAULT_MODEL` sourcing from `process.env.GEMINI_MODEL || 'gemini-2.5-flash'` to respect active cognitive settings.
  - Refined the Triage prompt to clearly distinguish when to use `TIER1_LITE`, `TIER2_FLASH`, and `TIER3_HEAVY`. Specifically, file/command tasks (like listing directories or checking projects) are routed to `TIER3_HEAVY`.
  - Added a `translatedCommand` property in the triage JSON. If `TIER3_HEAVY` is chosen, the triage model translates the command immediately, eliminating the separate command-translation API request.
  - Enriched the direct API (TIER1/TIER2) call with the `State Ledger Context` and `Attached File Metadata`.
- Modified [FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md):
  - Documented Single-Pass Command Triage & Translation, Enriched Execution Node Context, and Dynamic Model Selection.

## What Worked
- Routing is more robust and prevents hallucinations where simple-looking filesystem commands were triaged to `TIER1_LITE` which has no shell access.
- Substantial latency savings by collapsing triage and command translation into a single LLM API turn.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The gateway execution tier now accurately receives rulebook, state ledger context, and metadata even when running light tasks.
