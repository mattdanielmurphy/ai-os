# Agy CLI Permission Preference

- Matt specified that local `agy` CLI invocations should always include `--dangerously-skip-permissions` so headless tool calls do not stall on approval prompts.
- Added the standing behavior to `.rules/core_safety.md`, the shared source used across agent runtimes, and rebuilt generated instructions with `scripts/build_rules.py`.
- Verified the rule appears in Codex, Gemini, Claude, and Hermes instructions. The preference applies to CLI only; MCP remains preferred when its bridge is available.
