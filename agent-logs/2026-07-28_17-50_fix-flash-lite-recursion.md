## Goal
Investigate and fix an issue where the agent mistakenly invoked `Model: "flash"` instead of `Model: "flash_lite"` for file edits, and then fix a recursive subagent loop caused by the rule ambiguity.

## User Feedback & Decisions
The user noted that the previous fix caused an endless recursive loop. Decided to prefix the subagent prompt with `[LEAF AGENT: DO NOT RE-DELEGATE]` and instruct it to edit directly.

## Changes Made
- Modified `/Users/matt/projects/ai-os/.rules/gemini_only.md` to explicitly forbid using `Model: "flash"` and strongly enforce `Model: "flash_lite"` in the `invoke_subagent` arguments.
- Ran `build_rules.py` and `auto_commit.py` to compile and push.

## What Worked
- Prefixing the leaf agent prompt with `[LEAF AGENT: DO NOT RE-DELEGATE]` successfully stopped the recursion.
- Modifying the rule directly using the leaf agent.

## What Didn't Work / Known Issues
- The initial fix caused an infinite recursion because the subagent read the same "always delegate to subagent" rule.

## Architecture Notes
- Global rules apply to all subagents, so if a rule mandates delegation, leaf subagents must be explicitly instructed to break that rule to prevent recursion.
