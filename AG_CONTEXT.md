# Repository Context & Domain Knowledge

## Project Overview
`ai-os` is a local-first AI harness designed to transform a macOS machine into an editable, interactive database of thoughts, files, and automation.

## Core Directories & Structure
- `/bin`: Wrapper scripts and orchestrator binaries (e.g. `ai-os`, `agy`).
- `/docs`: Architecture, vision, memory, and strategy documentation.
- `/scripts`: Tool helper scripts (`mechanical_editor.py`, `get_last_cost.py`, `context_handoff.py`, `precision_edit.py`, `get-active-task.sh`, etc.).
- `/agent-logs`: Session engineering logs tracking goals, changes, and architecture discoveries.
- `/.devtool/features`: Features and user task specifications.

## Key Architecture & Domain Rules
- **Stable Anchor + Volatile Append Context Strategy:** Uses a structural map (repo map generated via AST parser/tree-sitter) as the stable front of the prompt context, and appends only active files and user requests at the end to maximize cache hits.
- **Delegation Philosophy:** agy handles work directly by default, using its native tools. When delegation makes sense (large context savings), agy prefers self-delegation (`agy -p`) over external tools like Claude Code to avoid per-call costs. Extreme delegation mode (always delegate to Claude Code) is preserved as a skill for when it's needed.
- **Dual-Rail Google Grid:** Seamlessly rotates Google accounts/authentication to double task quotas and VM limits.
- **Context Sync Protocol:** Userscript (`gemini.js`) integrated into browser/Tauri webview connects live Google web interface turns back to the Rust loopback daemon (`/api/context/sync`, `/api/notes/save`, `/api/revision/commit`) to serialize and version active text revisions in Git.
- **Three-Turn Delegation Protocol (Extreme Mode Only):** Available as the `agy-extreme-delegation` skill. Not the default — agy handles work directly with pragmatic self-delegation.
- **Hermes Thread Sync Daemon:** Integrates and synchronizes CLI/GUI NDJSON execution logs (`~/.gemini/antigravity-cli/brain/`) with Hermes' FTS5-enabled SQLite database (`~/.hermes/state.db`) bidirectionally. It launches as a background subprocess via the `bin/ai-os` execution wrapper, maintaining a unified search history across both platforms.
- **Hermes System Prompt Handoff**: Enabled the `agymcp` server to dynamically extract the active Hermes system prompt from `~/.hermes/state.db` and prepend it to prompts sent to `agy` (via `agy_tool`, `agy_continue_tool`, and `agy_start_tool`) to align instructions and preserve behavioral consistency during task handoffs.
