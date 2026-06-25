## Goal
Implement a Fail-Safe Circuit Breaker to handle quota drops or API dropouts without breaking the execution stream.

## Changes Made
- **Modified [ptyWrapper.js](file:///Users/matthewmurphy/projects/ai-os/src/ptyWrapper.js)**:
  - Enhanced `WarmPtySession` class with `currentTaskRejecter` to support promise rejection on execution errors.
  - Implemented live regex monitoring inside `onData` to catch `RESOURCE_EXHAUSTED`, `Quota Limit reached`, and `Baseline model quota reached`.
  - Automatically closes the PTY process and rejects the active promise with an `"AGY_QUOTA_DEPLETED"` error when a depletion pattern is found.
- **Modified [index.js](file:///Users/matthewmurphy/projects/ai-os/src/index.js)**:
  - Created `checkAgyHealth()` helper that parses `~/.gemini/antigravity-cli/settings.json` locally to check for baseline quota depletion.
  - Integrated `checkAgyHealth()` in the pre-flight check to proactively bypass the PTY wrapper.
  - Handled `AGY_QUOTA_DEPLETED` errors in the execution loop to switch instantly and cleanly to the Direct API Fallback executor.
- **Modified [FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md)**:
  - Added documentation describing the Fail-Safe Circuit Breaker subsystems (Proactive Check, PTY Stream Sniffing, Graceful Fallback).

## What Worked
- Proactive check accurately detects depleted state from mock settings files.
- Live stream sniffer successfully catches `RESOURCE_EXHAUSTED` markers, terminates the process, and raises the custom error.
- Catch block seamlessly triggers fallback routes.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Checking `settings.json` takes under 1ms and avoids wasting flat-rate tokens on dead sessions, protecting against cold boot latency.
- Rejecting the promise from the PTY session allows the main wrapper loop to act immediately when the stream fails.
