# Repository Context & Domain Knowledge

## Project Overview
`ai-os` is a local-first AI harness designed to transform a macOS machine into an editable, interactive database of thoughts, files, and automation.

## Core Directories & Structure
- `/bin`: Wrapper scripts and orchestrator binaries (e.g. `ai-os`, `agy`).
- `/docs`: Architecture, vision, memory, and strategy documentation.
- `/scripts`: Tool helper scripts (`subagent.py`, `get_last_cost.py`, `context_handoff.py`, `precision_edit.py`, `get-active-task.sh`, etc.).
- `/agent-logs`: Session engineering logs tracking goals, changes, and architecture discoveries (for agents).
- `/DEVELOPMENT_JOURNAL.md`: Human-readable timeline of key decisions and pivots (for the user).
- `/.devtool/features`: Features and user task specifications.

## Key Architecture & Domain Rules
- **AI Clipboard Memory Tool (Usage: search-clipboard '<query>' [--pro])**: Agents can search macOS Alfred clipboard history using natural language by running ⚡ Flash model found no confident match. Auto-escalating to Gemini 2.5 Pro...

=== AI Search Results for '<query>' ===
No matching items found by AI. non-interactively in terminal. Supports URL pre-filtering, brand alias expansion (e.g. g.co, gemini.google.com), and auto-escalation to Gemini 2.5 Pro.
- **Stable Anchor + Volatile Append Context Strategy:** Uses a structural map (repo map generated via AST parser/tree-sitter) as the stable front of the prompt context, and appends only active files and user requests at the end to maximize cache hits.
- **Delegation Philosophy:** agy handles work directly by default, using its native tools. When delegation makes sense (large context savings), agy prefers self-delegation (`agy -p`) over external tools like Claude Code to avoid per-call costs. Extreme delegation mode (always delegate to Claude Code) is preserved as a skill for when it's needed.
- **Dual-Rail Google Grid:** Seamlessly rotates Google accounts/authentication to double task quotas and VM limits.
- **Context Sync Protocol:** Userscript (`gemini.js`) integrated into browser/Tauri webview connects live Google web interface turns back to the Rust loopback daemon (`/api/context/sync`, `/api/notes/save`, `/api/revision/commit`) to serialize and version active text revisions in Git.
- **Three-Turn Delegation Protocol (Extreme Mode Only):** Available as the `agy-extreme-delegation` skill. Not the default — agy handles work directly with pragmatic self-delegation.
- **Hermes Thread Sync Daemon:** Integrates and synchronizes CLI/GUI NDJSON execution logs (`~/.gemini/antigravity-cli/brain/`) with Hermes' FTS5-enabled SQLite database (`~/.hermes/state.db`) bidirectionally. It launches as a background subprocess via the `bin/ai-os` execution wrapper, maintaining a unified search history across both platforms.
- **Hermes System Prompt Handoff**: Enabled the `agymcp` server to dynamically extract the active Hermes system prompt from `~/.hermes/state.db` and prepend it to prompts sent to `agy` (via `agy`, `agy_continue`, and `agy_start`) to align instructions and preserve behavioral consistency during task handoffs.
- **Multi-Tier Triage Routing & Pre-Flight Quota Check**: Evaluates remaining quota using `ag-quota -j` (or `codexbar status`). Automatically switches Antigravity to Minimal-Token Mode (Strict Orchestrator Mode 3) if remaining quota is low (<25%) or burning quickly, delegating code generation to `claude code` or cheap LiteLLM/subagent models.
- **Documentation & Wiki Architecture (6 Boundaries + Quartz Wiki):** Documentation is partitioned into 6 distinct boundaries: (1) AI-OS Core Project Docs (`~/projects/ai-os/docs/`), (2) Me & Personal (`Obsidian/Personal/`), (3) Mac System Specs (`Obsidian/Mac/`), (4) Personal Notes & Ideas (`Obsidian/Ideas/`), (5) Project Conceptual Specs (`Obsidian/Projects/<Name>/`), and (6) Implementation Code Docs (`~/projects/<Name>/docs/`). The unified off-the-shelf **Quartz 4.0 Wiki Engine** aggregates these boundaries and is served locally on `http://localhost:3333` via `ai-os wiki` or `ai-os-wiki`.


