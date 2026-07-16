## Goal
Find out why the global GEMINI.md file keeps disappearing and stop it from happening.

## Changes Made
- Restored `~/.gemini/GEMINI.md` from the most recent backup `~/.gemini/GEMINI.bak`.
- Modified `scripts/mechanical_editor.py` to correctly rename `.bak` files using `md_path.with_name(md_path.name + ".bak")` instead of `.with_suffix(".bak")` which stripped `.md`.
- Added an auto-recovery pre-check to `scripts/mechanical_editor.py` that restores `.bak` files if the original file is missing, handling hard crashes securely.
- Deleted older corrupted `.bak` files (`GEMINI.md.bak`, `GEMINI.bak.md`).

## What Worked
- Re-running `mechanical_editor.py` correctly delegated to Claude Code while protecting the context rules, and successfully renaming/restoring the original `GEMINI.md` without dropping its suffix or permanently hiding the file.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The `mechanical_editor.py` wrapper uses a `try/finally` block to hide `GEMINI.md` and `CLAUDE.md` from Claude Code's context loader. If the script was forcefully killed (e.g. SIGKILL), the `finally` block would never execute, leaving the file hidden as a `.bak`. The new auto-recovery check on script startup ensures it will resume properly even after an abrupt termination.
[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/d6e172c1-4990-4784-8677-c5b4745bd56e/.system_generated/logs/transcript.jsonl)