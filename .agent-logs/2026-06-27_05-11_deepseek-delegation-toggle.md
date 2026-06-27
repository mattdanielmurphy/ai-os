## Goal
Implement a dynamic toggle to let the user bypass DeepSeek delegation when they have plenty of quota, updating .zshrc_aios, GEMINI.md, and CLAUDE.md.

## Changes Made
- Modified `/Users/matthewmurphy/.zshrc_aios` to add `AIOS_DELEGATE` environment variable and `delegate_on`/`delegate_off` aliases.
- Updated `~/.gemini/GEMINI.md` to define a new Write Constraint (Triage Editing System) section that checks delegation status via `echo $AIOS_DELEGATE` and selects either Scenario A (using `mechanical_editor.py`) or Scenario B (Premium Speed Mode using Quoted Heredoc safely with `EOF_SAFE`).
- Synced the updated write constraint rules to `/Users/matthewmurphy/projects/ai-os/CLAUDE.md`.
- Documented changes in `/Users/matthewmurphy/projects/ai-os/FEATURES.md`.

## What Worked
- Configuration in .zshrc_aios is successfully created.
- Rule integration in GEMINI.md and CLAUDE.md successfully completed.
- Added feature documentation and committed changes.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- Checking `echo $AIOS_DELEGATE` allows the agent to decide between delegating to `mechanical_editor.py` and writing code directly using safely-quoted heredocs.
