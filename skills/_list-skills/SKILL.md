---
name: _list-skills
description: List all of Matt's skills newest first, with his own skills separated from stock ones (Hermes bundle, Claude app, plugins). Use when Matt types /_list-skills, asks what skills he has, wants to browse or find a skill, or forgot a command's name (including /coord).
argument-hint: [optional search word, or "mine" / "stock"]
---

# List skills

Run the lister and show its markdown output as your reply, unchanged:

```bash
python3 ~/projects/ai-os/scripts/list_skills.py
```

Arguments:
- a search word → add `--find "<word>"` (matches names and descriptions)
- `mine` → add `--mine`; `stock` → add `--stock`

Don't add commentary beyond one line if something looks off (e.g. a skill
of his landed under stock). "Mine" means anything in `~/.claude/skills` that
isn't in Hermes' bundled/web-UI manifests, plus his claude.ai account skills
and his ai-os mods; dates are when the SKILL.md was first created on this Mac.
