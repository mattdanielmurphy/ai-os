# Shelf

Things that are paused, not deleted. Nothing in `shelf/` is compiled into agent rules or synced as a skill.
To bring something back, follow its "Revive" note below.

| Shelved | Item | Why | Where it is now | Revive |
|---|---|---|---|---|
| 2026-10-17 | **agy / Antigravity delegation** (rules, agymcp, `agy`/`agy-extreme-delegation`/`hermes-to-agy` skills) | Antigravity trial ended; quota near zero | `shelf/rules/*.md` (agy sections), `shelf/skills/agy*`, `shelf/skills/hermes-to-agy`. Scripts still in `scripts/` (`handover.py`, `triage_router.py`, `subagent.py`, `swap_turn.py`, `gemini_antigravity_bridge.py`) and `services/agy-proxy` | Move the rule sections back into `.rules/<file>.md`, `mv shelf/skills/<name> skills/`, then `python3 scripts/build_rules.py` |
| 2026-10-17 | **query_aios planner** (`_plan-with-ai-os` and planner rules, :3031 companion) | Paused; Gemini web reliability | `shelf/rules/core_safety.md`, `gemini_only.md`, `codex_only.md`; `shelf/skills/_plan-with-*`. Code still in `scripts/query_aios.js`, `apps/query-aios-companion` | Same as above; start the companion with `la start aios-server` |
| 2026-10-17 | **Perplexity** | Endpoint removed | Mentions removed along with the query_aios sections | — |
| 2026-10-17 | **DeepSeek delegation** (`delegate-deepseek` skill) | Not in use | `shelf/skills/delegate-deepseek` | `mv shelf/skills/delegate-deepseek skills/ && python3 scripts/sync_skills.py` |
| 2026-10-17 | **LiteLLM proxy for Claude Code** (`ANTHROPIC_BASE_URL=http://localhost:8082`, model `deepseek-v4-flash`) | Claude Code now uses Anthropic directly | Backups: `~/.claude/backups/settings.json.pre-litellm-removal-2026-10-17`, `~/.claude/backups/zshrc.pre-litellm-removal-2026-10-17`; commented-out line in `~/.zshrc` | Restore those two backups |
| 2026-10-17 | **Hermes agent** (`hermes_only.md` rules, `HERMES.md` build, `hermes-*` skills) | Experiment; no longer used; schema could change under us | `shelf/rules/hermes_only.md`, `shelf/skills/hermes-*`. `~/.hermes/` untouched. **Still used read-only** by `scripts/threads.py` for old threads until they're migrated to markdown (see PROJECT_BOARD) | Move `hermes_only.md` back to `.rules/`, restore the HERMES block in `scripts/build_rules.py` (git history, 2026-10-17) |

Notes
- Claude-specific compiled rules (`claude_only.md`: per-turn preflight/postflight/auto_commit, `handover.py`) were also shelved; Claude now reads the lean `~/.claude/CLAUDE.md`.
- Each `shelf/rules/<file>.md` holds the exact sections removed from `.rules/<file>.md`.
