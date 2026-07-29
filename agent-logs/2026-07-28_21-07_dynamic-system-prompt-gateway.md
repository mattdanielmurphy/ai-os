# Agent Work Log: Dynamic System Prompt & Unified Triage Gateway

## Goal
Implement the Dynamic System Prompt & Unified Triage Gateway architecture across ai-os platforms (Antigravity, Hermes, Claude Code, agy) to eliminate system prompt bloat (~40k+ tokens) and rule drift.

## User Feedback & Decisions
- User approved the architectural implementation plan.
- User requested to skip using the `jules` CLI binary due to interactive TUI hanging non-interactive agent sessions.

## Changes Made
- **Created `.rules/` Modular Rules**:
  - `core_safety.md`
  - `git_protocol.md`
  - `agent_logs.md`
  - `subagent_leaf.md`
  - `mac_env.md`
- **Created `scripts/compile_dynamic_prompt.py`**: Dynamic system prompt compiler that assembles minimal, context-tailored prompts based on agent role (orchestrator vs leaf) and prompt keywords.
- **Updated `scripts/triage_task.py`**: Integrated `compile_prompt` to output `compiled_system_prompt` profile.
- **Updated `scripts/build_rules.py`**: Updated static rule bundler to generate lean baseline fallbacks for offline platforms.
- **Updated `scripts/preflight.py`**: Added dynamic system prompt compilation status display.

## What Worked
- Subagents now receive paper-thin leaf prompts (~600 tokens) with zero orchestrator bloat.
- Main orchestrator prompt size reduced significantly (~900 words).
- All tests and preflight checks pass cleanly.

## Architecture Notes
- Single source of truth remains in `.rules/` modular files.
- `compile_dynamic_prompt.py` generates on-demand prompts for both local turns and subagent invocations.
