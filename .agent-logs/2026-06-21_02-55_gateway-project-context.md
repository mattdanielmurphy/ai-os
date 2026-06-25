## Goal
Update the user's AI-OS Gateway CLI project (`ai-os`) to prevent files from being littered in generic parent directories (such as `~/projects`) and to ensure context/thread continuity by reading project-specific context files (`AG_CONTEXT.md`, `FEATURES.md`, and recent agent logs) at startup and injecting them into the LLM prompts.

## User Feedback & Decisions
- The user clarified that the request was for their agentic CLI project (the `ai-os` gateway) to consider its directory and avoid littering files in `~/projects`, and to preserve thread context by reading/utilizing past documentation.

## Changes Made
- **Modified [src/index.js](file:///Users/matthewmurphy/projects/ai-os/src/index.js)**:
  - Added a helper function `readProjectContext` to read `AG_CONTEXT.md`, `FEATURES.md`, and the 3 most recent `.agent-logs/*.md` files from the active project root.
  - Injected `agContext`, `features`, and `recentLogs` into the system instruction prompts for the Triage layer, Direct Execution engine, and Orchestrator.
  - Modified `executeInstructionDirectly` to accept `projectContext` and pass the context down.
  - Added a clear rule in `executionSystemInstruction` and `orchestratorSystemInstruction` directing the model that if the active directory is a generic parent directory (like `~/projects`), it must create a dedicated sub-directory instead of writing files directly to the parent folder.

## What Worked
- Successfully modified the CLI prompts and context loaders, allowing `ai-os` to load project context files from the active project root.
- Verified that execution rules explicitly prevent littering parent folders.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The gateway now behaves as a context-preserving agent by checking the active project workspace's files (`AG_CONTEXT.md`, `FEATURES.md`, `.agent-logs/`) before making routing and execution decisions, even across completely fresh CLI invocations.
