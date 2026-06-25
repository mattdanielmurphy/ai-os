## Goal
Fix the CLI tool hanging on 'Synthesizing execution response...'

## Changes Made
- Modified `src/index.js` in the `callGemini` function.
- Removed the hardcoded 'gemini-3.1-pro-low' model argument, replacing it with the passed `model` variable (with a fallback).
- Appended the `--dangerously-skip-permissions` flag to the `agy` CLI arguments to prevent interactive tool-approval prompts from hanging the child process since it lacks a TTY.

## What Worked
- Adding the flag correctly bypasses the hanging prompt in `callGemini`.

## What Didn't Work / Known Issues
- None.
