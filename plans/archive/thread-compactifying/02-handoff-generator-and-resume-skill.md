# Step 02: Handoff Generator and `/resume` Skill

## Goal
Generate `./tmp/context_handoff.md` and define the `/resume` skill for fresh thread restoration.

## Target Files
- `scripts/context_handoff.py`
- `~/.gemini/config/skills/resume/SKILL.md`

## Requirements & Detailed Specifications
- `context_handoff.py` writes concise markdown summary of active task, decisions, files modified, and next steps.
- `/resume` skill loads `context_handoff.md` + `AG_CONTEXT.md` in turn 1 of the new thread.

## Verification Criteria
- Run `context_handoff.py` and verify `./tmp/context_handoff.md` content.
