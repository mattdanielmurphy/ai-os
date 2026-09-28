# Dynamic Hook-Based Policy System for AI-OS & Codex

## Overview
AI-OS replaces the previous 24 KB monolithic global `~/.codex/AGENTS.md` bundle with an event-driven, hook-based architecture.

## Why Hooks Replace Monolithic Prompts
1. **Probabilistic Failure of Prompts**: Prompt instructions alone cannot guarantee safety. Under complex contexts, LLMs will occasionally run `rm -rf` or `cat .env`. `PreToolUse` hooks intercept tool calls at the OS execution boundary and deterministically block forbidden actions.
2. **Context Pollution in Casual Chats**: Ephemeral chats (e.g. asking for recipes, trivia, or chocolate recommendations) previously inherited thousands of tokens of Git rules, span-only markdown constraints, and personal IDs. The `UserPromptSubmit` hook classifies queries using a 3-tier router, ensuring casual chats run with zero token overhead (< 1ms).
3. **Decoupled from `preflight.py`**: The hook system operates standalone and does not invoke slow network calls, git fetches, or transcript indexing.

## Directory Structure
- `scripts/codex_hooks/`:
  - `classifier.py`: 3-tier routing and policy assembly engine (Tier 0 fast gate < 1ms, Tier 1 policy slicer 5-15ms, Tier 2 conditional Mem0).
  - `tool_guard.py`: Deterministic AST & shell token security filter (evaluates raw shell, dict payloads, and JS AST calls like `tools.exec_command` and `tools.read_file`).
  - `on_user_prompt.py`: CLI adapter for `UserPromptSubmit`.
  - `on_pre_tool_use.py`: CLI adapter for `PreToolUse`.
  - `rollout.py`: Rollout phase manager (`shadow`, `enforce`, `disabled`, `--enable-mem0`, `--disable-mem0`).
  - `rollback.py`: Instant 1-second recovery tool.
  - `test_hooks.py`: 35-case automated test and benchmark suite (100% pass rate).
- `~/.codex/policies/` & `config/codex_policies/`: Pre-compiled policy packs:
  - `policy_git.md`: Git detection & protocol.
  - `policy_reminders.md`: Apple Reminders protocol.
  - `policy_music.md`: Apple Music links and Canada catalog resolver.
  - `policy_personal_ids.md`: Zero-placeholder user identity metadata.
  - `policy_frontend.md`: Span-only styling and UI architecture.
  - `policy_agy_delegation.md`: Codex macOS orchestration and thin handoff.
  - `policy_database.md`: VPS database infrastructure.
  - `policy_skills_authoring.md`: Custom skills conventions.
  - `policy_rules_engine.md`: System directive persistence.
  - `policy_dev_workflow.md`: Work logs, journal, search-to-memory.

## Mem0 Benchmark & Latency Policy
- **Measured Cold-Start Latency**: 2,028.36ms (~2.03s) using Hermes Agent venv Python (`/Users/matt/.hermes/hermes-agent/venv/bin/python`). Warm query average: 1,858.26ms.
- **Hook Timeout Budget**: Codex's `hooks.json` timeout is set to 3.0s (3000ms). Synchronous vector search on every prompt risks timeout under load.
- **Latency Decision**: Mem0 semantic recall on prompt submission is gated behind `enable_mem0_on_prompt: false` by default in `~/.codex/hooks_config.json`.
- **Fast-Gate Execution**: Casual chats and standard development prompts execute in 0.06ms to 15ms. When enabled via `python3 rollout.py --enable-mem0`, vector search runs only on explicit personal context triggers with a strict 2.5s sub-budget timeout.

## Configuration & Rollout
- Active configuration file: `~/.codex/hooks_config.json`.
- Audit logs: `~/.codex/hooks_audit.log`.
- Hooks registration: `~/.codex/hooks.json` & `~/.codex/config.toml` (`[features] hooks = true`).
- Commands:
  - `python3 scripts/codex_hooks/rollout.py --status`
  - `python3 scripts/codex_hooks/rollout.py --mode shadow`
  - `python3 scripts/codex_hooks/rollout.py --mode enforce`
  - `python3 scripts/codex_hooks/rollout.py --enable-mem0` / `--disable-mem0`
  - `python3 scripts/codex_hooks/rollback.py`
