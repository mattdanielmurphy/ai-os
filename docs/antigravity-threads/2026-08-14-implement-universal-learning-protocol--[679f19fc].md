---
title: "Implement Universal Learning Protocol"
date: "2026-08-14"
conversation_id: "679f19fc-7c10-4571-9fc9-3f1c6a100174"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please make the following changes across the system to implement the Universal Learning Protocol and Global AI-OS Context:

1. Update `/Users/matt/.gemini/GEMINI.md`:
Add a dedicated section `# AI-OS Knowledge & Universal Learning Protocol`:
- Explain cross-workspace awareness: AI-OS scripts live in `/Users/matt/projects/ai-os/scripts/` (`preflight.py`, `postflight.py`, `auto_commit.py`, `learn_from_moment.py`).
- No-Edit Guardrail for Built-in Skills: Agents must NEVER mutate built-in or plugin skills in `~/.gemini/antigravity/builtin/` or `~/.gemini/config/plugins/`.
- Knowledge Routing Hierarchy:
  - Domain rules & persistent operational knowledge -> `./AG_CONTEXT.md`
  - Narrative timeline / decisions -> `./DEVELOPMENT_JOURNAL.md`
  - Conceptual/Entity knowledge across 6 boundaries -> `~/projects/ai-os/wiki/` (wiki-engine)
  - Custom skills & reusable workflows -> `~/.gemini/config/skills/` or `~/projects/ai-os/skills/custom-skills/<skill-name>/SKILL.md` (which are auto-synced via `watch_skills.sh`).

2. Create `/Users/matt/projects/ai-os/scripts/learn_from_moment.py`:
Implement a script that:
- Accepts `--trigger` (str), `--context` (str), and optional `--cwd` (defaults to current dir).
- Contains:
  - `resolve_repo_root(cwd: str) -> Path`: traverses up to find `.git` or `AG_CONTEXT.md`.
  - `guard_skill_path(path: Path) -> Path`: validates that any target skill path is inside `custom-skills` or `~/.gemini/config/skills`, raising `PermissionError` if an attempt is made to edit built-in plugins or system-bundled skills.
  - `classify_destination(context: str) -> list[str]`: classifies into `DOMAIN_RULE`, `NARRATIVE_DECISION`, `CONCEPTUAL_ENTITY`, or `REUSABLE_PROCEDURE`.
  - `append_learning_event(event_data: dict)`: appends to `agent-logs/learning-events.jsonl` (ensuring dir exists).
  - Handles writing or providing exact guidance for updating `AG_CONTEXT.md`, `DEVELOPMENT_JOURNAL.md`, or creating a custom skill in `skills/custom-skills/<slug>/SKILL.md`.
- Ensure it is executable with a shebang `#!/usr/bin/env python3`.

3. Create `/Users/matt/projects/ai-os/skills/custom-skills/learn-from-this-moment/SKILL.md`:
Create the skill definition with YAML frontmatter:
```yaml

---
name: learn-from-this-moment
description: Activates when the user asks an agent to learn from the current moment, conversation, or decision. Captures insights into persistent AI-OS memory tiers without touching built-in skills.
triggers:
  - "learn from this moment"
  - "learn from this"
  - "remember this for future agents"
  - "remember this"
custom: true
---
```

Provide clear instructions on the 4 knowledge destinations, how to invoke `python3 /Users/matt/projects/ai-os/scripts/learn_from_moment.py`, and the strict rule against modifying built-in skills.

4. Update `/Users/matt/projects/ai-os/AG_CONTEXT.md`:
Add a bullet under `## Key Architecture & Domain Rules` explaining the Universal Learning Protocol and the 4-tier knowledge persistence destinations (`AG_CONTEXT.md`, `DEVELOPMENT_JOURNAL.md`, Wiki Engine, and `skills/custom-skills/`).

5. Create `/Users/matt/projects/ai-os/tests/test_learn_from_moment.py`:
Add unit tests verifying `resolve_repo_root`, `guard_skill_path`, classification heuristics, and event logging.

</span>



<span title="Responded at 3:18am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Successfully implemented the Universal Learning Protocol and Global AI-OS Context as requested. All files have been created/updated and verified with passing unit tests.

### Implementation Summary
*   **GEMINI.md**: Added the requested knowledge protocol section.
*   **learn_from_moment.py**: New script for capturing insights (implemented with repository root resolution, path safety guardrails, and classification).
*   **SKILL.md**: New skill definition created at `~/projects/ai-os/skills/custom-skills/learn-from-this-moment/SKILL.md`.
*   **AG_CONTEXT.md**: Added documentation for the protocol.
*   **tests**: Added and passed unit tests in `~/projects/ai-os/tests/test_learn_from_moment.py`.
You can now use the new learning capability by invoking the script directly.

</span>



</span>

</span>