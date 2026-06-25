## Project Overview
- **Vision:** A local AI-Operating System Gateway on macOS that serves as a high-performance token firewall, deterministic safety layer, and cost-optimization framework. 
- **Core Problem:** Standard agentic architectures waste substantial token budgets by continually re-ingesting raw console logs, build telemetry, and redundant source file contents over long threads.
- **The Solution:** This project sits as a local Node.js proxy layer between the user and AI execution tiers. It abstracts heavy file-system grunt work into zero-token native metadata signatures, manages state locally across isolated threads, and leverages consumer flat-rate subscriptions out-of-band to maximize intelligence at near-zero operating costs.

## Architecture & System Topology
The system enforces a strict hierarchical topology where cognitive capacity matches task difficulty, heavily insulating high-cost models.

```text
       ┌────────────────────────────────────────────────────────┐
       │             User Custom Terminal Interface             │
       └───────────────────────────┬────────────────────────────┘
                                   │ (Raw Intent + File Flags)
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │   Local Gateway Wrapper (Mac System/Node.js Runtime)   │
       └─────┬─────────────────────┬──────────────────────┬─────┘
             │                     │                      │
   [0-Token Metadata]      [Circuit Breakers]    [Permission Intercepts]
             │                     │                      │
             ▼                     ▼                      ▼
┌───────────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│     Tier 1 (Lite)     │ │  Tier 2 (Flash)   │ │  Tier 3 (Elite)   │
│   Gemini Flash-Lite   │ │ Gemini 3.5 Flash  │ │  Antigravity CLI  │
│  Structural Parsing   │ │ Executive Triage  │ │ Heavy Refactoring │
│  & Build Filtering    │ │   & Macro-Plans   │ │ Warm PTY Session  │
└───────────────────────┘ └───────────────────┘ └───────────────────┘

```

### Key Subsystems

1. **0-Token Metadata Extractor:** Uses native Node.js filesystem utilities (`fs`) to scan referred file blocks. It extracts file size, line metrics, and small structural arrays of the first/last 5 lines, preventing thousands of tokens of raw code from bleeding into the initial model context.
2. **Deterministic Tool Layer & Path Jail:** Enforces file-system safety in hardcoded code rather than prompts. Completely replaces all file deletion strings with a safe migration script mapping to the macOS native trash directory (`~/.Trash/`). Programmatically sandboxes file write privileges to designated project domains.
3. **Runaway Log Slicer & Process Watchdog:** Protects the token loop budget. Shell commands are piped through a strict line buffer capping total data returns (max 50 lines / 10KB). Enforces an absolute 15-second hardware child-process timeout to catch and kill unexpected infinite loops.
4. **Warm PTY Multiplexer:** Eliminates CLI boot lags. Uses `node-pty` to run a persistent background interactive session of the `agy` CLI under the user's active flat-rate subscription. It accepts programmatic input via `stdin` and reads context completions via `stdout` chunk monitoring.
5. **State & Version Control:** Manages dual local trackers (`rulebook.md` and `state_ledger.json`) to allow immediate thread disconnection. Automatically executes background technical commits (`git add . && git commit`) upon task completions.
6. **Suggestion Integration:** Uses `get_suggestions` tool to pull pending feature requests or fixes from `~/.ai-os/suggestions.json`.

## Core Directives for Working Agents

If you are an agent modifying this project, you must strictly adhere to the following execution contract:

* **Separation of Routing Powers:** The Triage Layer (`gemini-2.5-flash`) must never output commands or execute bash scripts directly. Its sole responsibility is generating a clean routing schema JSON and passing the instruction package to the designated target tier.
* **The Permission Gate:** You are completely forbidden from writing silent modifications or additions to `rulebook.md`. You must utilize the `modify_rulebook` tool, which explicitly triggers a manual user prompt intercept in the local shell environment.
* **Decisive Intuition:** When you encounter ambiguity in layout or technical implementation, do not pause to ask minor clarifying questions. Take the initiative to choose a clean, industry-standard approach, and declare that action explicitly using a visible `[Decision Log]` format in your output.
* **Chronological Log Rotation:** Keep active session contexts lean. Always read `AG_CONTEXT.md` and scan only the **most recent two log files** inside `.agent-logs/` to piece together current workspace history, querying older historical blocks using targeted search utilities only when explicitly necessary.
* **Suggestion-First Workflow:** Whenever the user or context references "suggestions" or "pending tasks," you must immediately execute the `get_suggestions` tool. Prioritize resolving these items to maintain the system's evolution according to the user's recorded intent.

## Tooling Documentation
### get_suggestions
- **Description:** Retrieves all unresolved entries from the global `~/.ai-os/suggestions.json` file.
- **Usage:** `node src/tools/get_suggestions.js`
- **Output:** A JSON array of suggestion objects.

## Environment & Paths
- Obsidian Personal Notes: /Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/
- Personal Notes: ~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/
- User Projects Root: /Users/matthewmurphy/projects/
- ai-os: /Users/matthewmurphy/projects/ai-os
- AI-OS: /Users/matthewmurphy/projects/ai-os
- Suggestions File: ~/.ai-os/suggestions.json
