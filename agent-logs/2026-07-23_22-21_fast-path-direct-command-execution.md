## Goal
Prevent `triage_router.py` from needlessly starting `agy` or triggering LLM models when invoked with simple deterministic system/OS commands (e.g. `python3 triage_router.py 'open google chrome'`).

## User Feedback & Decisions
- Direct OS commands like `open google chrome` must execute instantly without running any model or launching `agy`.

## Changes Made
- Added `try_direct_execution` in `scripts/triage_router.py` to intercept simple OS actions:
  - Application opening (`open <app>`, `launch <app>`, `start <app>`) with aliases for Chrome, Spotify, Visual Studio Code, Calculator, System Settings, Safari, Terminal, etc.
  - URL and file/directory opening.
  - Process termination (`pkill`, `killall`).
  - Text-to-speech (`say`).
  - Shell command execution (`run`, `exec`).
- Updated argument extraction to join non-flag positional arguments.
- Added fast-path unit tests in `scripts/test_triage.py`.

## What Worked
- Running `python3 /Users/matt/projects/ai-os/scripts/triage_router.py 'open google chrome'` instantly opened Google Chrome via `open -a "Google Chrome"` in milliseconds with zero LLM/agy overhead.
- Passed `test_triage.py` unit checks cleanly.

## Architecture Notes
- Direct execution bypasses Tier 1 and Tier 2 LLM triage completely when matching deterministic command intent.
