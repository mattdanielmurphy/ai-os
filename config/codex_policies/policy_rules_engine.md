# Proactive System Directive & Knowledge Persistence
- **Rule**: When Matt establishes a permanent workflow preference, tool routing rule, or operational invariant (e.g. "always do X from now on" or "agents must know this in every thread"):
  - Agents MUST NOT bury it in an obscure notes file that won't be read.
  - Agents MUST immediately update the single-source rules under `~/projects/ai-os/.rules/` and run `python3 ~/projects/ai-os/scripts/build_rules.py` so the directive is compiled into `GEMINI.md` and `CLAUDE.md` across every future session.
  - **Scope is global by default (2026-10-20)**: Any rule or preference Matt gives applies everywhere: every project, thread, Code session, Claude Projects, and every agent (Claude, Gemini, Codex), unless he explicitly limits it to one project or thread. NEVER ask him which scope he means; save it globally (here, `~/.claude/CLAUDE.md`, and the current project's instructions when one exists).
