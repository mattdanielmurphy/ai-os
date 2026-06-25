## Goal
Implement a Dynamic Clarification State in the Tier 2 Triage model's schema to prompt the user during ambiguity, and enforce budget constraints (`[BUDGET_MODE: LEAN]` or `[BUDGET_MODE: ARCHITECTURAL]`) in the execution layers.

## Changes Made
- **Modified [index.js](file:///Users/matthewmurphy/projects/ai-os/src/index.js)**:
  - Upgraded `triageSystemInstruction` system prompt with `requires_clarification`, `clarification_message`, and `clarification_options` JSON schema parameters.
  - Implemented interactive console prompts in `processGatewayRequest` when `decision.requires_clarification` is true.
  - Mapped selection to `LEAN` or `ARCHITECTURAL` budget mode.
  - Injected choice selection into `sanitized_directive` explicitly so execution models can read the user choice in the prompt.
  - Passed `budgetMode` to `executeInstructionDirectly` and PTY Orchestrator loop system instructions.
  - Enforced `maxIterations = 1` for PTY Orchestrator and `maxActions = 2` for Direct Executor when `LEAN` mode is selected.
- **Modified [FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md)**:
  - Documented the Dynamic Clarification State & Budget Boundary Variables feature.

## What Worked
- Interactive menu prompts trigger and halt gateway execution successfully when ambiguity is identified.
- Options selection maps cleanly to boundary variables (`[BUDGET_MODE: LEAN]` vs `[BUDGET_MODE: ARCHITECTURAL]`).
- Loop/action constraints are correctly applied (completes in single iteration under `LEAN` mode).

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Injecting the choice explicitly into the `sanitized_directive` prompt string ensures the target models receive it in the user context, resolving any disconnect from system instruction overrides.
