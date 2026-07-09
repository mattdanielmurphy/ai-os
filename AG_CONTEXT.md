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
- **Triage Editing System ($AIOS_DELEGATE):** Toggled to delegate complex code editing tasks to LiteLLM/mechanical_editor or execute directly using Quoted Heredocs when speed is preferred.
- **Dual-Rail Google Grid:** Seamlessly rotates Google accounts/authentication to double task quotas and VM limits.
- **Context Sync Protocol:** Userscript (`gemini.js`) integrated into browser/Tauri webview connects live Google web interface turns back to the Rust loopback daemon (`/api/context/sync`, `/api/notes/save`, `/api/revision/commit`) to serialize and version active text revisions in Git.
