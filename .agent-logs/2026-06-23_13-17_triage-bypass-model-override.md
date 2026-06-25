## Goal
Provide a way to run the AI-OS Gateway that overrides any complexity and triage logic and specifies exactly what model to use to accomplish the task.

## Changes Made
- `src/index.js`:
  - Added CLI argument parsing for `--model=<model>`, `--model <model>`, and `-m <model>`, mapping to a top-level `cliModel` variable.
  - Updated `/settings model [value]` command within the TUI REPL handler to also update `cliModel`, bypassing triage for subsequent interactive queries.
  - Modified `processGatewayRequest` to accept an optional `modelOverride` parameter.
  - Implemented triage bypass when a model override is present, routing directly to the Gemini Direct API executor.
  - Updated `executeInstructionDirectly` signature and implementation to accept and pass the model override down to `callGemini` instances.
  - Passed the model override to the final response explanation synthesis.
- `FEATURES.md`:
  - Added documentation for the new "Triage Bypass & Custom Model Direct Execution" feature.

## What Worked
- Passing `--model gemini-2.5-flash` successfully bypassed the triage protocol and routed the instruction directly to the Direct API executor using `gemini-2.5-flash`.
- Bypassing the triage model and PTY orchestrator significantly reduced token cost and latency for direct runs.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Direct execution completely avoids the warm background PTY session orchestration loop, utilizing `executeInstructionDirectly` and making atomic tool queries directly using the specified model.
