---
name: resume
description: Restores context from `./tmp/context_handoff.md` and `AG_CONTEXT.md` on fresh thread start after context compactifying or thread reset.
---

# Resume Skill Instructions

When the user types `/resume` or requests restoring context on a fresh thread start:

1. **Inspect Handoff Context Artifact:**
   - Immediately check for `./tmp/context_handoff.md` in the current project root.
   - Read `./tmp/context_handoff.md` to load the current active task goals, decisions made, changed files/git state, active plan status, and immediate next steps.

2. **Read Project Context & Recent State:**
   - Read `AG_CONTEXT.md` at the project root for core architectural facts and conventions.
   - Check `plans/<plan-name>/status.json` or `.devtool/features/*.md` if referenced in the handoff file to confirm current step status.

3. **Verify Git Environment:**
   - Perform a quick single git check (`git status --porcelain`) to confirm the working directory matches the handoff file state.

4. **Resume Execution Seamlessly:**
   - Directly resume execution of the immediate next step without asking redundant questions or requiring the user to re-explain the task.
   - Output a brief 2-sentence summary to the user acknowledging context restoration and declaring the immediate action being taken.
