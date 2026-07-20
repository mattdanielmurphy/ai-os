[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-ide/brain/4c029b2f-e424-4e9b-b563-1ec578e6d0b2/.system_generated/logs/transcript.jsonl)

## Goal
Identify why the global `GEMINI.md` rules file keeps disappearing/getting deleted and prevent it from recurring.

## Changes Made
- Restored `~/.gemini/GEMINI.md` from the backup at `~/.gemini/GEMINI.bak`.
- Added a safety check to `scripts/sync_rules.sh` to skip rsync if the source rules file `~/.gemini/GEMINI.md` is empty/0 bytes but the target file `.gemini/GEMINI.md` exists and is not empty.
- Created `.devtool/features/fix-gemini-md-disappearing.md` tracking the bug fix and transitioned it to `status: "review"`.

## What Worked
- Restoring `~/.gemini/GEMINI.md` from `GEMINI.bak` successfully brought back the rules.
- The `git status` hook and watcher automatically synced the restored rules back to the workspace.
- The safety check prevents silent overwriting of non-empty workspace rules files with blank files in the future.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- The shell environment intercepts git commands and terminal startups to run `scripts/sync_rules.sh`, which performs a one-way rsync from `~/.gemini/GEMINI.md` to `.gemini/GEMINI.md`.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-ide/brain/4c029b2f-e424-4e9b-b563-1ec578e6d0b2/.system_generated/logs/transcript.jsonl)
