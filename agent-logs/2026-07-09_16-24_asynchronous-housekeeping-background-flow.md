## Goal
Implement a background housekeeping script (`scripts/housekeep.py`) to handle agent log generation and automatic git commits asynchronously so that task outputs can be presented immediately to the user.

## User Feedback & Decisions
- User requested that the agent show output immediately as soon as the main part of the task is done, and run housekeeping (like git commit and log generation) in the background.
- Proceed without waiting for plan approval unless it is substantial.

## Changes Made
- Created `scripts/housekeep.py` to write agent logs and call `auto_commit.py`.
- Updated `.agents/AGENTS.md` with guidelines on how to run background housekeeping asynchronously and handle wakeups.
- Updated `docs/FEATURES.md` to ledger this new feature.

## What Worked
- Script parses command-line arguments and stdin logs.
- Automatic Git commit successfully stages and commits all changes.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Running commands asynchronously with low `WaitMsBeforeAsync` allows the orchestrator to respond immediately, ending the turn while the commit process runs in the background. When the background process finishes, the agent gets woken up and can output a simple confirmation without interrupting the user's focus.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-ide/brain/b9548a4a-7dd4-4b5a-b4a0-8b151119630b/.system_generated/logs/transcript.jsonl)
