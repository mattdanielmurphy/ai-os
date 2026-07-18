## Goal
Build the DeepSeek v4 Flash Low Triage/Routing System. Automatically default sessions to a fast model and enable agents to run structured, non-interactive handovers to more powerful models for complex tasks.

## User Feedback & Decisions
The user approved the implementation plan and asked to proceed.

## Changes Made
- Modified `scripts/handover.py` to support `--non-interactive`, `--to-model`, `--completed`, `--next-steps`, and `--discoveries` arguments.
- Updated `bin/ai-os` wrapper to append `--model claude-haiku-ds-v4-flash-low` by default if no `--model` argument is passed.
- Added `agy` wrapper function to `.zshrc_aios` to default to `--model claude-haiku-ds-v4-flash-low` for direct CLI calls.
- Updated `AGENTS.md` and `CLAUDE.md` to define Model Triage and Handoff Rules.
- Documented the changes in `FEATURES.md` and transitioned the feature task frontmatter status to `review`.

## What Worked
- `handover.py` successfully parses command-line arguments and handles non-interactive model execution logic.
- Wrapper scripts correctly default to the cheap model.
- Handover logic correctly replaces the process.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The fast model serves as the entry point and executes a non-interactive `handover.py` script to seamlessly escalate to a pro model for complex task sections.