## Goal
Clean up scripts, relocate legacy Tauri-only scripts to `legacy-tauri-gui/scripts/`, fix credential-reading logic in `get_last_cost.py` (since token path had changed), and update global and project-level GEMINI.md system rules to explicitly enforce delegating editing tasks to subagents/scripts to conserve premium parent-agent token quota.

## User Feedback & Decisions
- Concurred with the user's preference to strictly limit parent-agent direct editing to only super trivial edits (specifically, single contiguous edits to small files where the exact edit point is already known) to prevent token context window blowout.
- Refined the core rules to document this cost conservation logic so future agents will inherit it at startup.

## Changes Made
- **Relocated files**:
  - Moved `fix_terminal.py` -> `legacy-tauri-gui/scripts/fix_terminal.py`
  - Moved `spare_engine.js` -> `legacy-tauri-gui/scripts/spare_engine.js`
- **Modified files**:
  - [scripts/get_last_cost.py](file:///Users/matt/projects/ai-os/scripts/get_last_cost.py): Pointed `TOKEN_PATH` to `~/.gemini/oauth_creds.json` and adjusted JSON structure query. Removed the unauthorized client credentials refresh routine.
  - [~/.gemini/GEMINI.md](file:///Users/matt/.gemini/GEMINI.md): Appended Rule 10 detailing strict Telemetry Prohibitions and Task Delegation rules (mandating delegation to cheaper subagents unless the edit is contiguous, single, and on a small file with a known edit point).
  - [.gemini/GEMINI.md](file:///Users/matt/projects/ai-os/.gemini/GEMINI.md): Mirrored the updated Rule 10.

## What Worked
- Tauri scripts successfully moved out of the root `scripts/` directory.
- `get_last_cost.py` successfully resolved OAuth credentials locally and defaults gracefully to N/A without throwing HTTP errors or failing.
- Global and local rules updated and synced.

## What Didn't Work / Known Issues
- Direct desktop-oauth refresh in `get_last_cost.py` fails due to missing `client_secret` required by Google's OAuth endpoints for desktop apps, so the script only functions as long as the IDE's active token is valid. This is acceptable since agents are now prohibited from running it.
