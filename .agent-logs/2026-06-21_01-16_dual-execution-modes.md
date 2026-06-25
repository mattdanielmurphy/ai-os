## Goal
Implement two execution modes for the Sentinel AI-OS Gateway:
- **User Mode:** Hides verbose telemetry, displaying only high-level progress stages and a clean, styled box-drawing interface wrapping user queries and final cognitive responses.
- **Debug Mode:** Displays detailed telemetry (file extraction details, triage decision routing, version control actions, warm PTY wrapper logs) in dimmed, low-contrast terminal styles to distinguish the system noise from the user inputs and final responses.

## Changes Made
- Created `src/logger.js`:
  - Formulated a standard `GatewayLogger` wrapper class supporting `debug`, `info`, `warn`, `error`, `showQuery`, and `showResponse` channels.
  - Designed `drawBox` function utilizing standard ANSI terminal escape sequences and word-boundary safe-wrapping to draw high-contrast, premium styled boxes around user queries and gateway responses.
- Refactored `src/index.js`:
  - Integrated `GatewayLogger`.
  - Moved CLI arguments parsing to the module root.
  - Integrated command-line flags (`--mode=user`/`--mode=debug`, `--user`, `--debug`) and `.env` parsing (`GATEWAY_MODE`) to set execution modes.
  - Refactored output logs to quiet down standard telemetry under `logger.debug` and present progress via `logger.info`.
- Modified `src/ptyWrapper.js` & `src/circuitBreaker.js`:
  - Injected the logger instance into `WarmPtySession` and `FinancialGovernor` constructors to route status reports and financial safety alerts cleanly.
- Updated `FEATURES.md`:
  - Documented the Dual Execution Modes capability and configuration.

## What Worked
- High-level progress status displays clearly and dynamically in User Mode.
- Output boxes correctly wrap long text prompts/responses on word boundaries without breaking layout structures.
- Quiet telemetry (in dimmed gray colors) is easily skipped by the human eye in Debug Mode, making it easy to spot the main message frames.

## What Didn't Work / Known Issues
- Currently, when executing a task via the direct Gemini API node, the file content of an attached file is not forwarded in the API payload itself. Only the user query is sent. For future tasks, passing a combined payload (metadata + user query) when files are attached will prevent direct nodes from asking the user to provide file contents manually.

## Architecture Notes
- Using ANSI escape code `\x1b[90m` (bright black/gray) is an effective way to dim CLI messages on modern macOS Terminal clients, making them functionally invisible unless explicitly read.
