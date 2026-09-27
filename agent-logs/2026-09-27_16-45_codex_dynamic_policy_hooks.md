# AI-OS Agent Log: Codex Dynamic Policy Hooks Engine

- **Date**: 2026-09-27 16:45 MDT
- **Context**: Dynamic Codex policy engine implementation in ai-os replacing static monolithic `~/.codex/AGENTS.md`.

## Summary of Changes
1. **Minimal Global Instructions (`compile_dynamic_prompt.py`)**:
   - Replaced the static ~24 KB `AGENTS.md` bundle with a minimal 19-line global baseline in `~/.codex/AGENTS.md` (preserved monolithic backup at `~/.codex/AGENTS.md.bak`).
2. **Domain Policy Packs**:
   - Compiled modular policy packs into `~/.codex/policies/` and `config/codex_policies/` (`policy_git`, `policy_reminders`, `policy_music`, `policy_personal_ids`, `policy_frontend`, `policy_agy_delegation`, `policy_database`, `policy_skills_authoring`, `policy_rules_engine`, `policy_dev_workflow`).
3. **Sub-Millisecond Classifier (`scripts/codex_hooks/classifier.py`)**:
   - Implemented 3-tier routing:
     - Tier 0: Fast regex/CWD gate for casual queries (< 0.2ms, 0 extra tokens).
     - Tier 1: Domain-specific policy pack slicing for active repositories and matching topics.
     - Tier 2: Conditional Mem0 fact recall via `aios-memory` backed by the Hermes venv.
4. **PreToolUse Execution Guardrails (`scripts/codex_hooks/tool_guard.py`)**:
   - Built deterministic shell and AST token parser blocking destructive commands (`rm`, `rmdir`, `find -delete`, `find -exec rm`), secret file inspections (`.env*`, `*credentials*`, private keys), forbidden package managers (`npm`, `pnpm`, `yarn`), root `git init ~`, and system `/tmp`.
   - Properly implemented Codex JSON wire schema: returning `continue: true` with `decision: "block"`, `reason`, and `hookSpecificOutput: { hookEventName: "PreToolUse", permissionDecision: "deny" }`.
5. **Rollout & Rollback Management (`rollout.py`, `rollback.py`)**:
   - Built rollout CLI supporting `shadow`, `enforce`, and `disabled` modes with automated schema installation (`install_hooks()`) and status reporting.
   - Built 1-second instant rollback tool restoring `AGENTS.md.bak` and disabling hooks.
6. **Automated Verification Suite (`test_hooks.py`)**:
   - 30/30 automated tests passing covering classifier latency, policy slicing, AST guardrails, shadow mode transitions, and CLI stdin/stdout wire protocols.
