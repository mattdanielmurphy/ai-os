# Plan-to-Implementation Default

- Updated `skills/_plan-with-ai-os/SKILL.md` and the local Antigravity workflow so a successful plan is implemented in the same task by default.
- The agent should infer routine decisions from Matt's stated preferences and project conventions, asking only when a material ambiguity or consequential architectural decision cannot be resolved safely. Explicit plan-only requests and existing planner hard stops remain unchanged.
- Updated `.rules/codex_only.md` and `.rules/core_safety.md`, rebuilt generated rules, and ran `scripts/sync_skills.py`.
- Verification: reviewed the focused diff and confirmed planner dispatch, GitHub-origin checks, recovery, and fallback instructions were preserved. No code tests were applicable to this instruction-only change.
