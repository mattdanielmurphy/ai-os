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
| 2026-10-17 | **Mem0 memory** (`aios-memory`, `_manage-memory` skill, Search-to-Memory rule) | Only 20 memories, nothing wrote to it after Sept 25; replaced by QMD search over the vault and all threads | `shelf/skills/_manage-memory`, `shelf/rules/core_safety.md` (old rule). Data still in `~/.mem0/`; `scripts/aios_memory.py` kept; `preflight.py` memory call stubbed | `mv shelf/skills/_manage-memory skills/`, restore the rule section, remove the `return 0, []` line in `get_memory_data`, then `python3 scripts/build_rules.py && python3 scripts/sync_skills.py` |

Notes
- Claude-specific compiled rules (`claude_only.md`: per-turn preflight/postflight/auto_commit, `handover.py`) were also shelved; Claude now reads the lean `~/.claude/CLAUDE.md`.
- Each `shelf/rules/<file>.md` holds the exact sections removed from `.rules/<file>.md`.

## Git history scrub (2026-10-17)
Personal identifiers (phone, student IDs, ASN, BC PEN, DOB, CCID) were replaced with `[REDACTED-…]` across all history and force-pushed. Every commit hash changed.
The pre-scrub `.git` is at `~/.Trash/ai-os-pre-scrub-2026-10-17/old.git` (still contains the PII; gone once Trash is emptied). It is the only copy of these local-only branches, dropped from the new clone:
`agy-mcp/job-5b9db406c2c64d67`, `agy-mcp/job-bf22ed13c9b94653`, `agy-mcp/job_1786255018_92ee67d1f728`, `agy-mcp/job_1786255217_556103ba1234`, `agy-mcp/job_1786264321_4309dcaad738`, `agy-mcp/job_1786264963_5697699b24a5`, `agy-mcp/job_1786265406_7c8803be59fc`, `agy-mcp/job_1786951443_4d3cc173683c`, `archive/custom-tauri`, `archive/macos-app`, `old`, plus 2 stashes from agy jobs.
The worktrees under `.agy-mcp/worktrees/` and `~/.codex/worktrees/*/ai-os` pointed at the old `.git` and no longer work.
