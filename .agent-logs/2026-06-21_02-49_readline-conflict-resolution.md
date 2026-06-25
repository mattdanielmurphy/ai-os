## Goal
Resolve the character duplication and input leakage bug when answering clarification prompts within the interactive REPL.

## Changes Made
- **Modified [index.js](file:///Users/matthewmurphy/projects/ai-os/src/index.js)**:
  - Created `askQuestion` helper to prompt the user for input. It reuses the active `readline` interface if passed, or falls back to creating a temporary one.
  - Updated `processGatewayRequest` to accept `rlInterface` as an optional third parameter.
  - Replaced inline temporary `readline` interface instantiations in the clarification stage and the self-reflection audit loop with calls to `askQuestion`.
  - Paused the main REPL `readline` interface using `rl.pause()` before running `processGatewayRequest`, and resumed it with `rl.resume()` inside a `finally` block to prevent duplicate key event processing and stdin collision.
- **Modified [FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md)**:
  - Documented the Readline Conflict Resolution details in the Dynamic Clarification State section.

## What Worked
- Reusing the active `readline` interface resolved the key duplication bug (where typing a single character registered as double keystrokes, e.g. "1" -> "11").
- Pausing the active REPL interface during query execution ensures that keystrokes typed during processing are not leaked back to the main REPL loop as fresh commands.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- In Node.js, multiple active `readline` interfaces listening to the same `process.stdin` stream simultaneously will duplicate input stream reads and keypress events. Pausing the main interface and reusing it via `rl.question` temporarily takes exclusive control of the stream without spawning new conflict-prone instances.
