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

# Learn From This Moment

This skill allows you to capture insights and persist them into the AI-OS memory tiers.

## Knowledge Destinations
1. **DOMAIN_RULE**: Append to `AG_CONTEXT.md` for persistent operational rules.
2. **NARRATIVE_DECISION**: Append to `DEVELOPMENT_JOURNAL.md` for decision history.
3. **CONCEPTUAL_ENTITY**: Update the Wiki engine (`~/projects/ai-os/wiki/`).
4. **REUSABLE_PROCEDURE**: Create or update a custom skill in `~/projects/ai-os/skills/custom-skills/<slug>/SKILL.md`.

## How to use
Invoke the learn script with:
```bash
python3 /Users/matt/projects/ai-os/scripts/learn_from_moment.py --trigger "<user_trigger>" --context "<what_to_remember>"
```

## Guardrails
- **NEVER** modify built-in or plugin skills in `~/.gemini/antigravity/builtin/` or `~/.gemini/config/plugins/`.
- Only use `custom-skills/` or `~/.gemini/config/skills/` for your own reusable workflows.
