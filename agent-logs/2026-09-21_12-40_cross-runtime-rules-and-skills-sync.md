# Cross-runtime rules and skills synchronization

- Found Codex's global `/Users/matt/.codex/AGENTS.md` empty even though `.rules/` already generated Hermes, Gemini/Antigravity, and Claude instruction files.
- Added Codex to `build_rules.py`; Codex now receives the shared core safety, Git, and agent-log rules from the same compiler.
- Fixed `sync_skills.py` so repository-owned skill paths always propagate from `skills/`; target-only vendor skills remain untouched.
- Verified all 203 repository skill entrypoints match across Hermes, Claude, `~/.agents` (Codex's installed skill source), Gemini, agy, and Antigravity.
