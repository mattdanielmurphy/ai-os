---
name: ai-os-rule-management
description: Edit .rules/ sources and rebuild platform instruction files.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ai-os, rules, system-instructions, build-rules, documentation]
    related_skills: [build, plan]
---

# ai-os Rule Management

## Overview

The `~/projects/ai-os/.rules/` directory is the **single source of truth** for global agent system instructions that affect all platforms (Hermes, Claude Code, Gemini/agy, Codex). Editing `.rules/` and running `build_rules.py` regenerates CLAUDE.md, HERMES.md, and GEMINI.md — the files that get baked into every agent's system prompt at session start.

**Do NOT edit the generated files directly.** Always edit the source in `.rules/` and rebuild.

## When to Use

- You implemented a new capability that changes how agents should work (new protocol, new CLI flag, routing change, new subagent mode)
- The user corrected you about where a global instruction belongs
- You need to add a pitfall, guardrail, or cross-platform note that every agent should see
- You're adding a platform-specific rule for `hermes_only.md`, `claude_only.md`, or `gemini_only.md`

## File Layout

| File | Purpose |
|------|---------|
| `.rules/common.md` | Rules shared by EVERY agent. Agent-behavior rules go here. |
| `.rules/hermes_only.md` | Hermes-specific tools and guardrails |
| `.rules/claude_only.md` | Claude Code-specific (autotick, Prettier, etc.) |
| `.rules/gemini_only.md` | Gemini/agy-specific (quota, Antigravity CLI, CM.md) |
| `AG_CONTEXT.md` | **Per-project** — domain knowledge about this repo, not agent behavior |
| `FEATURES.md` | Feature list for the current project |

## `.rules/` vs `AG_CONTEXT.md`

| `.rules/common.md` (use this) | `AG_CONTEXT.md` (avoid for agent rules) |
|---|---|
| How agents should work (protocols, commands, routing) | What this project does (directory layout, architecture) |
| Behavioral rules, guardrails, pitfalls | Domain knowledge, key decisions, history |
| Cross-platform instructions | Project-specific context |

**When in doubt, use `.rules/common.md`.** It's what every agent sees at session start. `AG_CONTEXT.md` only reaches agents that read it explicitly.

## Workflow

1. **Edit the source file** in `.rules/` (use patch or write_file).

2. **Rebuild all platform files**:
   ```bash
   python3 ~/projects/ai-os/scripts/build_rules.py
   ```
   Regenerates: `CLAUDE.md`, `HERMES.md` (in-repo + `~/.hermes/`), `~/.gemini/GEMINI.md`, `AGENTS.md` (symlink). Also runs `sync_skills.py`.

3. **Verify** the generated files show the new content.

4. **Commit** both `.rules/` edits AND the regenerated files:
   ```bash
   git add .rules/ CLAUDE.md HERMES.md AGENTS.md
   python3 ~/projects/ai-os/scripts/auto_commit.py
   ```

## Common Pitfalls

1. **Editing `AG_CONTEXT.md` for agent-behavior rules.** It's project context, not system instructions. Agent rules belong in `.rules/common.md`.

2. **Editing generated files directly.** `CLAUDE.md` / `HERMES.md` / `GEMINI.md` are all rebuilt by `build_rules.py`. Manual edits get overwritten.

3. **Forgetting to run `build_rules.py`.** Source edits alone don't reach any agent until the target files are regenerated.

4. **Committing only `.rules/` without regenerated outputs.** Both source and generated files are tracked in git. Commit them together.

5. **Updating only one platform's generated file manually.** Always rebuild all platforms with `build_rules.py`.

## Verification Checklist

- [ ] Rule added/edited in `.rules/common.md` (or platform-specific variant)
- [ ] `python3 ~/projects/ai-os/scripts/build_rules.py` run
- [ ] Generated files verified to contain the new content
- [ ] `git add` includes both `.rules/` edits AND regenerated files
- [ ] Changes committed and pushed