## Goal
Fix the PTY session hang and execute the user's actual intention inside the warm PTY session instead of just echoing a placeholder.

## Changes Made
- Modified `src/ptyWrapper.js`:
  - Refactored `start()` to return a Promise that resolves when the custom prompt is matched, with a 5000ms watchdog timeout to prevent hanging.
  - Added a 10000ms watchdog timeout to `executeCommand()` to prevent commands from hanging the entire gateway.
  - Created and exported `cleanPtyOutput(output, command)` utility to strip command echoing and prompt noise from the PTY stdout.
  - Updated default `cliCommand` to `'export PS1="Ready for input> " && bash --norc --noprofile -i'` to run an interactive bash subshell with a custom, deterministic, clean prompt.
- Modified `src/index.js`:
  - Updated `ptySession` construction to use default constructor settings (clean interactive bash).
  - Properly awaited `ptySession.start()` before writing commands.
  - Implemented dynamic shell command translation via `gemini-2.5-flash` in `TIER3_HEAVY` mode, translating the user's natural language request into a precise shell command.
  - Used `cleanPtyOutput` to clean command results before printing and storing.
  - Tracked API spend for translation.
- Updated `FEATURES.md`:
  - Documented dynamic command translation, PTY promise synchronization, and clean output parsing.

## What Worked
- PTY startup and commands resolve reliably and without racing.
- The user's natural language request (e.g. "list the files in this dir") was correctly translated to `ls` and executed.
- Echoed command text and terminal prompt were stripped cleanly from the final result.

## What Didn't Work / Known Issues
- None. The implementation works cleanly and efficiently.

## Architecture Notes
- Using `bash --norc --noprofile -i` keeps stdout clean of control characters and profile-specific ANSI sequences, allowing simple substring prompt matching.
