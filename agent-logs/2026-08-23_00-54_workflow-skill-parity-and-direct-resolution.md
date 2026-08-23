# Workflow & Skill 1:1 Parity and Direct Resolution Protocol

## Summary
Persisted behavioral learnings from `/learn`: established strict 1:1 parity between global workflows (`~/.gemini/config/global_workflows/`) and custom skills (`~/projects/ai-os/skills/`), and mandated direct path resolution to eliminate exploratory filesystem searches when referencing named workflows/skills.

## Details of Changes
1. **Created Missing Skills for 1:1 Parity**:
   - `skills/_plan-with-ai-os/SKILL.md` (mirrors `global_workflows/_plan-with-ai-os.md`)
   - `skills/rule/SKILL.md` (mirrors `global_workflows/rule.md`)

2. **System Rules Update (`.rules/core_safety.md`)**:
   - Added **Workflow & Skill 1:1 Parity Invariant**: All custom workflows must be co-located as first-class skills in `skills/<name>/SKILL.md`.
   - Added **Direct Skill/Workflow Resolution**: Mandated that agents immediately check `~/.gemini/config/global_workflows/<name>.md` and `~/projects/ai-os/skills/<name>/SKILL.md` directly rather than executing broad filesystem sweeps.

3. **Compilation & Multi-Way Synchronization**:
   - Executed `scripts/sync_skills.py` to propagate new skills across all runtime environments (`~/.gemini`, `~/.claude`, `~/.hermes`, `~/.agents`, `~/.agy`).
   - Executed `scripts/build_rules.py` to recompile `GEMINI.md`, `CLAUDE.md`, `HERMES.md`, and `LEAF.md`.
