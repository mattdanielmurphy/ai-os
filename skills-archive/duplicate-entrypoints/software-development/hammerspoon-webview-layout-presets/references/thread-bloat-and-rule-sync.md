# Economic Thread Bloat & Multi-Engine Rule Sync

## 1. Thread Reset Economics ($T_{\text{hist}}$ vs $T_{\text{sys}}$)
When evaluating whether to reset a thread or spawn a subagent, use `scripts/check_thread_bloat.py`:

$$\mathbf{T_{\text{hist\_threshold}} = S + \frac{R - 1}{M} \cdot (T_{\text{sys}} + S)}$$

- **$T_{\text{sys}}$**: System baseline tokens (system rules, active skills, MCP tool definitions).
- **$T_{\text{hist}}$**: Accumulated conversation history tokens.
- **$R$**: Cache hit price ratio ($R = 4.0$, uncached input = $4\times$ cache hit cost).
- **$S$**: Handoff summary creation overhead ($S = 1000$ tokens).
- **$M$**: Estimated remaining turns ($M = 5.0$).

When $T_{\text{hist}} > T_{\text{hist\_threshold}}$, write a handoff summary to `agent-logs/` and trigger a fresh thread.

## 2. Multi-Engine Rule Synchronization
All core agent system instructions live in `~/projects/ai-os/.rules/` (`common.md`, `claude_only.md`, `gemini_only.md`, `hermes_only.md`).

Running `python3 /Users/matt/projects/ai-os/scripts/build_rules.py` (or `scripts/preflight.py`) automatically compiles:
- `CLAUDE.md` -> `~/projects/ai-os/CLAUDE.md`
- `GEMINI.md` -> `~/.gemini/GEMINI.md` (and symlinked to `AGENTS.md`)
- `HERMES.md` -> `~/projects/ai-os/HERMES.md` and `~/.hermes/HERMES.md`

This guarantees that Antigravity, Claude Code, and Hermes Agent always operate on identical base rules without overwriting Hermes' managed internal databases or user memories.
