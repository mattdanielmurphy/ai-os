# Custom Skills Naming & Authoring Invariant
- **Rule**: When creating, authoring, or refactoring personal/custom skills for Matt in `~/projects/ai-os/skills/` or environment skill directories:
  - **Leading Underscore Namespace (`_`)**: ALL user-authored/custom skills MUST begin with a leading underscore (`_`) prefix so they sort to the very top of alphabetical listings, IDE pickers, and autocomplete popovers.
  - **Action-First Semantic Naming (`_<action>-<constraint>`)**: Skill names MUST start with the primary action verb, followed by the defining behavioral constraint or modifier (e.g., `_critique-without-ghostwriting`, `_prune-subtractively`).
  - **Workflow & Skill 1:1 Parity Invariant**: ALL custom workflows under `~/.gemini/config/global_workflows/` (e.g. `_plan-with-ai-os`, `_plan-with-subagent`, `_plan-with-gemini`, `fast`, `audit`, `rule`) MUST be co-located as first-class skills in `~/projects/ai-os/skills/<name>/SKILL.md`.
  - **Direct Skill/Workflow Resolution**: When referencing or inspecting any named workflow or skill (e.g. `_plan-with-ai-os`), agents MUST NEVER perform broad filesystem searches or grep sweeps. Agents MUST check the direct paths:
    1. `~/.gemini/config/global_workflows/<name>.md`
    2. `~/projects/ai-os/skills/<name>/SKILL.md` (or `~/.gemini/config/skills/<name>/SKILL.md`)
  - **Auto-Sync Invariant**: After creating or updating any skill under `~/projects/ai-os/skills/`, agents MUST immediately execute `python3 /Users/matt/projects/ai-os/scripts/sync_skills.py` to propagate changes across all local agent runtimes (`~/.hermes`, `~/.gemini`, `~/.claude`, `~/.agents`).
