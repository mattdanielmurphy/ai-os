## Goal
Change the model triage and handoff rules to prevent blind executions, use Gemini pro by default for handoffs, run agents in tmux, and use agy exclusively when quota is abundant.

## User Feedback & Decisions
- The user feedback was that we should never run agents blind (i.e. avoiding `--non-interactive`, `--print` or background execution without attachment). Handoffs should be interactive so that the user can review and steer the spawned agent.
- Spawning subagents should attach to the active terminal or run in a visible tmux session.
- Under high agy quota, we should use agy exclusively for subagents rather than routing to other models like claude code.

## Changes Made
- Modified `AGENTS.md` and `CLAUDE.md` to update the **Model Triage and Handoff Rules** accordingly.

## What Worked
- Successfully edited both configuration files and ran git diff to verify.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Handoff rules are defined in both `AGENTS.md` and `CLAUDE.md`. Both must be kept in sync.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-cli/brain/a985ac84-cceb-4aeb-a824-aaed5dd58143/.system_generated/logs/transcript.jsonl)
