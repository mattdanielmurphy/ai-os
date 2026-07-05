# AI OS

Personal AI OS — a global CLI harness and desktop application for AI agent workspace automation.

## Features

- **Multi-Engine Support:** Choose between Deepseek V4 Flash (Claude Code) and Gemini (`agy`).
- **Workspace Automation:** Easily switch between active projects and manage sessions.
- **Triage Mode vs. Worker Bee Mode:** Advanced prompt routing system for handling tasks of varying complexity.

## Engine Modes (Triage vs. Worker Bee)

When submitting a prompt to the `agy` engine, you can toggle between **Triage Mode** and **Worker Bee Mode** using the "Pre-triage Mode" checkbox in the UI. Depending on the mode selected, the AI receives vastly different operational instructions.

### 1. Worker Bee Mode (Default)
When Pre-triage is unchecked, the agent operates in **Worker Bee Mode**. In this mode, the agent receives the full suite of system instructions and acts as a direct contributor.

**Key Characteristics:**
- Expected to write code directly, run terminal commands, and perform actions on the local filesystem.
- Receives strict rules on file editing (e.g., prohibiting `rm -rf`, enforcing code constraints, and requiring precise edits).
- Uses a local temporary folder (`./tmp`) to avoid permission prompts during file modifications.
- At the end of its session, it creates an `.agent-logs/` file mapping out the goal, changes, and architectural discoveries made during the execution.
- Capable of context self-healing by triggering automated handoffs for complex tasks.

### 2. Triage Mode
When Pre-triage is checked, the agent operates in **Triage Mode**. In this mode, the agent acts as an architectural supervisor and task delegator, not a direct coder.

**Key Characteristics:**
- Analyzes the user's prompt to determine if it is complex, multi-part, or requires a long-running process.
- Strictly prohibited from executing the coding tasks itself or modifying the codebase directly.
- Deconstructs the original request into a set of bounded, highly specific sub-tasks.
- Uses tools like `create_child_thread` (or equivalent sub-agent tools) to spawn fresh, scoped conversations for each sub-task. This prevents the primary context from snowballing out of control.
- Carefully preserves the user's original constraints, intent, quoted text, file paths, and explicit code blocks when delegating to subagents.
- Summarizes the results once the delegated subagents complete their work.

This mode should be explicitly toggled on for complex or extensive refactoring requests where delegating work to individual "worker bee" threads will yield cleaner results.

## Configuration & Customization
Historically, the system rules were defined globally via a `GEMINI.md` file. With the introduction of multi-mode prompt routing, the `GEMINI.md` file is intentionally left empty. The operational rules have been migrated to `src/systemPromptConfig.ts` within the AI-OS source code, enabling dynamic injection at runtime based on the selected mode.

## Architecture Overview

The ai-os workspace is composed of several key components:

- **Orchestration & Bootloading:** A shell-wrapping bootloader (`bin/ai-os`, `.zshrc_aios`) that intercepts destructive commands and injects quiet-run wrappers.
- **Tauri GUI & PTY Layer:** A React/TS frontend utilizing `xterm.js` to render multiplexed background processes via Rust bindings (`src/main.ts`, `src-tauri/src/main.rs`).
- **Cost & Quota Telemetry Engine:** Sub-model cost math and token refresh flows (`scripts/telemetry_db.py`).
- **Triage Editing System:** Surgical text mutations and LLM-driven patch applications (`scripts/precision_edit.py`, `scripts/mechanical_editor.py`).
- **Git Memory Pipeline:** Multi-layer indexing for safe history retrieval (`scripts/memory_search.sh`, `scripts/memory_diff.sh`).
- **Dynamic Rules Injection:** Manages context routing to active models and global rulesets (`scripts/append_system_rule.py`).
- **Automated Context Handoff:** Creates standardized context log files in `.agent-logs/` conforming to the Indexed Handoff Protocol (`scripts/context_handoff.py`).

### Roadmap & Planned Features
- **Rust API Bridge Layer:** Expanding Tauri `main.rs` to include HTTP server infrastructure for web-chat syncing and stateless revision loops.
- **Codebase Ingestion Parser (AST Upgrades):** Upgrading from regex/while-loop parsing to formal AST parsing (e.g., `tree-sitter`) for deeper code structure understanding.
- **Browser Extension / Web Context Sync:** Siphoning web sessions directly into the local repo.
- **Automated Auth Rotation Daemon:** Headless account-swapping component to rotate Google Accounts.
- **Semantic Thought Layer:** Integrating local vector embeddings and native macOS automation (JXA/AppleScript wrappers).

## Notes: Thought Log
I'm realizing; I really ought to have a robust task system, and see THAT instead of threads.
But I'm also realizing: isn't that exactly what that one claude code wrapper does? Has like robust projet management and kanban.
I think I was turned off by its complexity but honestly I think it'd be better to just learn to use that than to continue to work on this.
I mean; fuck, I don't know.
I like the idea of making my specific vision, you know?
But if it's open source I could fork it.
But I kind of just learned that I shouldn't rush into working on a fork because it's not likely to work exactly how I want. And there's a lot I've built already, several times... and to start over AGAIN is a HUGE DECISION.
Fuck, so I can't remember the specific one I had heard about before... but I did find https://github.com/BloopAI/vibe-kanban which looks pretty damn good.
Oh... it's so alluring