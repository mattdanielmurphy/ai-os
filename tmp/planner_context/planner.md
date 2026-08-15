---
name: planner
description: "MANDATORY: Initiate high-reasoning planning via agymcp (Gemini 3.1 Pro Low) before executing non-trivial tasks."
---

Run high-reasoning planning using the `planner` skill instructions in `/Users/matt/.gemini/config/skills/planner/SKILL.md`.

1. Do NOT inspect codebase files directly in the main thread.
2. Delegate context pre-fetching to a Flash subagent.
3. Call `agymcp:agy` (or `agymcp:agy_start`) with the specified model profile to author `implementation_plan.md`.
4. Store the returned `SESSION_ID` for Stage 4 QA audit resumption (`agymcp:agy_continue`).
