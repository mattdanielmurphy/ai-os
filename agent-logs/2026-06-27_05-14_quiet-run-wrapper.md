## Goal
Create a token-saving shell wrapper for noisy commands to protect the agent's context window.

## Changes Made
- Added a `qr` (Quiet Run) function to `/Users/matthewmurphy/.zshrc_aios` and `/Users/matthewmurphy/projects/ai-os/.zshrc_aios` that redirects all output of a command to `/tmp/aios_last_cmd.log` and returns success/fail summaries.
- Modified `/Users/matthewmurphy/.gemini/GEMINI.md` to add a new core rule instructing agents to use `qr` when running noisy commands.
- Updated `/Users/matthewmurphy/projects/ai-os/FEATURES.md` to document the new feature.

## What Worked
- Modifying both `.zshrc_aios` configs to support the `qr` command.
- Injecting the prompt guardrail into global rules in `GEMINI.md`.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The `qr` function returns the command's exit code, allowing shell operators like `&&` or `||` to function normally.
- By piping to `/tmp/aios_last_cmd.log`, we save massive amounts of context tokens from command outputs.
