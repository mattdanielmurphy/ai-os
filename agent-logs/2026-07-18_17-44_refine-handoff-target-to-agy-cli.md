## Goal
Refine model triage and handoff rules to ensure handoffs explicitly spawn the local `agy` CLI client (`antigravity-cli`) synchronously in the active terminal using `handover.py` rather than hitting an API endpoint.

## User Feedback & Decisions
- The user clarified that the handoff must target the local `agy` command-line executable directly, replacing the process and attaching it to the active terminal for interactive steering, instead of calling a remote API endpoint.

## Changes Made
- Updated `AGENTS.md` and `CLAUDE.md` to explicitly state that handoffs must spawn the local `agy` client using `handover.py` and attach to it interactively.

## What Worked
- Successfully edited both configurations and validated via git diff.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Handoff rules are defined in both `AGENTS.md` and `CLAUDE.md`. Both must be kept in sync.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-cli/brain/a985ac84-cceb-4aeb-a824-aaed5dd58143/.system_generated/logs/transcript.jsonl)
