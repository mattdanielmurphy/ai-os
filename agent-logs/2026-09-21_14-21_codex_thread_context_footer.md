# Codex Thread Context Footer Trial

- Added a ChatGPT/Codex-only response convention in `.rules/codex_only.md`.
- After the 100k context-token threshold, agents append a compact footer with an authoritative count when available, or the truthful fallback `100k+ (exact count unavailable)`.
- The trial does not automatically start a new task or interrupt work; it only surfaces context pressure for Matt to act on.
