# AI-OS Agent Log: Codex Dynamic Policy Engine Worktree Reconciliation & Mem0 Benchmark

- **Date**: 2026-09-27 22:00 MDT
- **Context**: Reconcile dynamic Codex policy engine state in worktree `/Users/matt/.codex/worktrees/da3d/ai-os`, verify wire schema & JS invocations, benchmark Mem0 latency, and expand test suite.

## Summary of Accomplishments

1. **Worktree Reconciliation & Dynamic Path Resolution**:
   - Reconciled worktree state on detached HEAD on top of `origin/main` (commit `6a054e7e`).
   - Updated `scripts/build_rules.py` and `scripts/compile_dynamic_prompt.py` to resolve `PROJECT_ROOT` dynamically using `git rev-parse --show-toplevel` so scripts operate correctly across primary checkouts and `.codex/worktrees/`.

2. **Empirical Cold Mem0 Benchmark & Prompt Gate**:
   - Identified Mem0 installation in Hermes Agent virtualenv (`/Users/matt/.hermes/hermes-agent/venv/bin/python`).
   - Measured cold-start latency: **2,028.36ms (~2.03s)**; warm query average: **1,858.26ms**.
   - Because Codex's hook timeout budget is 3.0s, synchronous Mem0 queries on every prompt risk timing out or causing noticeable lag.
   - Configured `enable_mem0_on_prompt: false` default in `~/.codex/hooks_config.json`, keeping Tier 0/1 prompt submission latency at **0.06ms - 15ms**.
   - Added `--enable-mem0` and `--disable-mem0` flags to `rollout.py` with 2.5s sub-budget timeout protection when enabled.

3. **Real-World Codex Wire Schema & JS AST Guardrail Support**:
   - Inspected Codex binary and historical session logs in `~/.codex/sessions/`.
   - Identified that Codex models frequently execute tools via JavaScript snippets in `exec`: `tools.exec_command({cmd: "...", workdir: "..."})` and `tools.read_file({path: "..."})`.
   - Upgraded `tool_guard.py` with multi-format token and AST regex extractors handling raw strings, dictionary payloads (`cmd`, `path`, etc.), and JS AST calls.

4. **Rollout & Rollback Upgrades**:
   - Enhanced `scripts/codex_hooks/rollout.py` to preserve existing configuration keys, record measured latency (2,028.4ms), and display Mem0 prompt state in `--status`.
   - Verified instant recovery mechanism (`scripts/codex_hooks/rollback.py`) for restoring monolithic `~/.codex/AGENTS.md.bak`.

5. **Expanded Verification Suite (`test_hooks.py`)**:
   - Added 5 new test cases verifying JS AST invocations (`tools.exec_command` with `rm -rf`, `cat .env`, `bun add`, and `tools.read_file` with `.env` vs `package.json`).
   - Achieved **35/35 passing tests (100% pass rate)**.
