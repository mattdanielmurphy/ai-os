## Goal
Add capability to persist optimization suggestions generated during the gateway's self-reflection loop to a global database (`~/.ai-os/suggestions.json`), and introduce CLI commands (`--suggestions`, `--resolve-suggestion=<id>`) and REPL commands (`/suggestions`, `/suggestions resolve <id>`) to list and resolve them one by one.

## User Feedback & Decisions
- The user requested suggestions to be saved globally somewhere along with context, so they can go through them one by one and the agent making the correction will have the full context needed.
- Decided to save them in `~/.ai-os/suggestions.json` and load target folder context automatically when executing a resolution.

## Changes Made
- **Modified [src/index.js](file:///Users/matthewmurphy/projects/ai-os/src/index.js)**:
  - Added helper functions to load, save, and append suggestions in `~/.ai-os/suggestions.json`.
  - Hooked suggestions into the self-reflection audit loop so that each new suggestion is given a unique ID, persisted globally, and displays its global ID on the console.
  - Implemented the `--suggestions` flag to list pending suggestions.
  - Implemented `--resolve-suggestion=<id>` which switches the active workspace path, loads the recommendation + original query context, triggers the execution engine, and marks the suggestion as resolved upon successful completion.
  - Implemented REPL commands `/suggestions` and `/suggestions resolve <id>`.
- **Modified [FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md)**:
  - Documented the new Global Suggestions Database & One-by-One Resolution features.

## What Worked
- Mocking a pending suggestion in `~/.ai-os/suggestions.json` and listing it via `node src/index.js --suggestions` worked perfectly.
- Running `--resolve-suggestion=1` correctly switched workspace target, loaded the prompt context, and started execution.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Suggestions are stored globally in the user's home directory under `~/.ai-os/suggestions.json` so they persist across multiple workspaces.
