# Plan With Subagent (`_plan-with-subagent`) Skill & Workflow Creation

## Summary
Created the `_plan-with-subagent` custom skill and workflow, providing a high-reasoning Gemini planning workflow via native subagent dispatch without requiring GitHub remote synchronization or out-of-band Perplexity routing.

## Details of Changes
1. **Created Custom Skill (`skills/_plan-with-subagent/SKILL.md`)**:
   - Defined high-reasoning planning protocol using `Gemini 3.7 Flash (High)`.
   - Direct local filesystem access for researching files, context, and logs.
   - Structured plan generation target at `<appDataDir>/brain/<conversation-id>/implementation_plan.md`.
   - Added `skills/_plan-with-gemini/SKILL.md` as an alias.

2. **Created Global Workflows (`~/.gemini/config/global_workflows/`)**:
   - Added `_plan-with-subagent.md` and `_plan-with-gemini.md` for slash command invocation (`/_plan-with-subagent`, `/_plan-with-gemini`).

3. **Multi-Way Skill Sync Robustness (`scripts/sync_skills.py`)**:
   - Hardened `sync_skills.py` against broken symlinks and non-file target collisions.
   - Synced the new skill across all runtime directories (`~/.hermes`, `~/.claude`, `~/.agents`, `~/.gemini`, `~/.agy`).

4. **Compiled System Rules**:
   - Executed `scripts/build_rules.py` to compile single-source rules across target platforms.
