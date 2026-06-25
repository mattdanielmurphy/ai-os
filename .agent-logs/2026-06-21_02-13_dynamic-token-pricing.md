## Goal
Provide accurate, real-time model cost calculations based on actual token usage per model, support dynamic pricing updates using the OpenRouter public API, and format token counts concisely (e.g. `21k` instead of `21091`).

## Changes Made
- **Created [pricing.js](file:///Users/matthewmurphy/projects/ai-os/src/pricing.js)**:
  - Fetches dynamic model pricing from `https://openrouter.ai/api/v1/models` in the background with a 2-second timeout to avoid blocking startups.
  - Implements local cached storage in `./tmp/pricing_cache.json` for fast startup lookup.
  - Configures fallback model prices for all standard Gemini models.
  - Added `calculateCost` to compute the exact price per model/prompt/completion tokens.
  - Added `formatTokens` to format counts like `21091` to `21k` and `950` to `950`.
- **Modified [circuitBreaker.js](file:///Users/matthewmurphy/projects/ai-os/src/circuitBreaker.js)**:
  - Updated `FinancialGovernor.recordSpend` to use `calculateCost` mapped to tier models instead of hardcoded estimations.
- **Modified [index.js](file:///Users/matthewmurphy/projects/ai-os/src/index.js)**:
  - Integrated `loadPricing` on IIFE startup.
  - Added global `threadCost` and `currentQueryCost` trackers.
  - Accumulated costs in `callGemini` using actual usage metadata.
  - Accumulated costs for simulated spends during triage, explanation, direct API, and agy runs.
  - Updated console metrics logger to print concise token counts and precise formatted query and thread costs.
- **Modified [FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md)**:
  - Added detailed documentation on token costing and concise formatting features.

## What Worked
- Fetching and parsing the OpenRouter API structure works correctly and successfully stores cache to `./tmp/pricing_cache.json`.
- Costs are calculated accurately for both actual usage metrics and simulated tier limits.
- Log outputs formatted correctly (e.g., `Query: 2.7k tokens | Cost: $0.0027`).

## What Didn't Work / Known Issues
- None. Offline fallbacks perform correctly and fall back to accurate defaults.

## Architecture Notes
- The gateway's native `autoCommit` functionality automatically commits changes to `src/` at the end of execution runs. The work log file and any remaining modifications (like `FEATURES.md`) will be committed manually to complete the session.
