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
