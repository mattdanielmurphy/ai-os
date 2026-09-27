# Proactive System Directive & Knowledge Persistence
- **Rule**: When Matt establishes a permanent workflow preference, tool routing rule, or operational invariant (e.g. "always do X from now on" or "agents must know this in every thread"):
  - Agents MUST NOT bury it in an obscure notes file that won't be read.
  - Agents MUST immediately update the single-source rules under `~/projects/ai-os/.rules/` and run `python3 ~/projects/ai-os/scripts/build_rules.py` so the directive is compiled into `GEMINI.md`, `CLAUDE.md`, and `HERMES.md` across every future session.
