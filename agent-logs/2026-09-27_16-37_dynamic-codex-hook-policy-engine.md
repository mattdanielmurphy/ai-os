# 2026-09-27 16:37 - Dynamic Codex Hook-Based Policy Engine Implementation

## Summary
Replaced the static 24 KB monolithic global `~/.codex/AGENTS.md` bundle with an event-driven, dynamic hook-based policy engine for OpenAI Codex and ChatGPT on macOS.

## Key Changes
1. **Source Compilation & Modular Policy Slicing**:
   - Updated `scripts/compile_dynamic_prompt.py` and `scripts/build_rules.py` to extract 10 modular policy packs (`policy_git`, `policy_reminders`, `policy_music`, `policy_personal_ids`, `policy_frontend`, `policy_agy_delegation`, `policy_database`, `policy_skills_authoring`, `policy_rules_engine`, `policy_dev_workflow`) into `~/.codex/policies/` and `config/codex_policies/`.
   - Generated an ultra-minimal global `~/.codex/AGENTS.md` (1.4 KB, 18 lines) containing only identity baseline, dynamic runtime notices, and orchestration boundaries.

2. **UserPromptSubmit Intent & Context Classifier (`scripts/codex_hooks/classifier.py`)**:
   - Implemented a 3-tier routing architecture:
     - **Tier 0 Fast Gate (< 1ms)**: Ephemeral, projectless chats (`~/Documents/Codex/...`) and casual queries bypass policy injection entirely, injecting 0 extra tokens (`additionalContext: null`).
     - **Tier 1 Policy Pack Slicer (5-15ms)**: Dynamically injects matching policy packs based on active Git repository context and prompt keywords.
     - **Tier 2 Conditional Mem0 Recall (30-60ms)**: Queries local Mem0 vector database (`aios_memory.py`) only when user preferences, setup history, or personal context could matter.
   - Decoupled completely from `preflight.py`.

3. **PreToolUse Deterministic Security Guardrails (`scripts/codex_hooks/tool_guard.py`)**:
   - Enforced hard execution gates:
     - Blocks `rm` and `rmdir` (allows `node_modules` exception; instructs `mv <path> ~/.Trash/`).
     - Blocks reads and inspections of `.env*`, `*credentials*`, `id_rsa`, `*.pem`, `*.key` (instructs `aios-env check`).
     - Blocks `npm`, `pnpm`, and `yarn` (instructs `bun`).
     - Blocks `git init` in the home root directory (`~`).
     - Blocks file output/creation in system `/tmp/` (instructs `./tmp/`).
     - Blocks bare file creation in generic parent container `~/projects/`.

4. **Rollout & Rollback Management (`scripts/codex_hooks/rollout.py`, `rollback.py`)**:
   - Backed up monolithic `AGENTS.md` to `~/.codex/AGENTS.md.bak`.
   - Built CLI tools for switching between `shadow` mode (logging to `~/.codex/hooks_audit.log` without blocking) and `enforce` mode (hard halts).
   - Built instant 1-second recovery tool `rollback.py`.
   - Registered hooks in `~/.codex/hooks.json` and enabled `features.hooks = true` in `~/.codex/config.toml`.

5. **Testing & Verification (`scripts/codex_hooks/test_hooks.py`)**:
   - Passed 27/27 automated unit and integration tests covering latency benchmarks (0.57ms casual gate), policy slicing, Mem0 recall, and all security guardrails.

## Verification
- `test_hooks.py`: 27/27 tests passed (100%).
- `codex debug prompt-input`: Verified minimal instructions load with zero prompt bloat.
