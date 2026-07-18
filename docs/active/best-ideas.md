# Architecture, Philosophy & Best Ideas Overview

This document synthesizes the core philosophies, architectural breakthroughs, and design ideas implemented across the `ai-os` codebase.

---

## 1. Core Philosophies

### Clean Workspace & Temporary Scripts
Single-purpose or one-off scripts should be directed to `/tmp` to prevent codebase pollution. As a future enhancement, we could store these scripts in a persistent global archive outside the workspace for reusability without cluttering project directories.

### Token Parsimony
Context windows are sacred resources. Rather than feeding an agent thousands of lines of raw code, `ai-os` prioritizes sending the minimal set of structural definitions (ASTs/Repo Maps) and limits full-file reads strictly to active workspace files.

### Cost & Quota Arbitrage
Premium reasoning models are used sparingly to orchestrate and design tasks, while commodity local or economical models perform execution (code construction, testing, logging). Quotas are preserved by rotating accounts and leveraging flat-rate subscriptions (e.g., Dual-Rail Google Grid) to keep paid API usage at a minimum.

### On-Request Autonomy
High-density context (hardware state, system applications, browser DOMs) is kept lazily-loaded. Agents query telemetry and environment statistics only when explicitly required by a task, preventing context ballooning.

---

## 2. Key Architectural Breakthroughs

### Stable Anchor + Volatile Append Context Strategy
Prompt context is divided into two distinct components:
1. **The Stable Anchor:** Static instructions, output constraints, and a highly compressed codebase map (class names, function signatures, folder layout without implementation logic). This section remains identical across calls to maximize caching.
2. **Volatile Append:** Raw text of the active files under modification, followed by the user request. Cache hits are preserved since edits at the end of the prompt do not invalidate the heavy structural anchor at the front.

### The 2D Collapsible Document Canvas & Progressive Disclosure
Linear scroll fatigue in terminals and chat logs is resolved by parsing markdown heading hierarchies (`#`, `##`) into a 2D interactive tree in the UI. 
- High-level headers act as concise, scannable summaries.
- Details and code blocks nested under `###` or deeper are collapsed by default and hydrated on-demand (either pre-rendered or via Just-in-Time agent sub-queries).

### Symmetrical Dual-Rail Google Grid
To double daily limits and bypass API concurrency bottlenecks, the Rust bridge and configuration layers automatically rotate credentials between two Google Pro accounts (**Rail Alpha** and **Rail Beta**). This extends to the rotation of developer keys, browser sessions, and the deployment of remote Google Jules VMs.

### Stateless Context Sync & Git Revision Slider
A single userscript (`gemini.js`) injected into the browser/Tauri webview intercepts turns in the Google web interface and posts clean `[AIOS_DOC]` payloads to a local Rust daemon at `127.0.0.1`.
- The Rust backend maps the session to a thread-specific Git worktree.
- Revisions are committed to Git version history automatically, preventing duplicate content from bloating chat logs.
- The Tauri UI provides a hardware-accelerated slider to scroll through Git diff versions of the active document pane.

---

## 3. Tooling & System Optimization

### Triage Editing System ($AIOS_DELEGATE)
Edits are dynamically routed based on the active delegate state:
- **Quota-Saving Mode (`AIOS_DELEGATE=true`):** Complex operations are handled by calling `mechanical_editor.py` to generate and apply unified patches via cheap local proxy endpoints.
- **Premium Speed Mode (`AIOS_DELEGATE=false`):** Direct edits are executed using Quoted Heredocs to bypass command escaping errors.
- **Fast-Path (`precision_edit.py`):** Multi-mode LLM-free programmatic appends, replacements, and insertions.

### Token-Saving Command Interception & Wrappers
- **`qr` (Quiet Run):** Pipes noisy commands (e.g. `npm install`, `cargo build`) to a temporary log, returning a token-efficient success indicator or the last 20 lines on failure.
- **`read_lines`:** Extracts precise line ranges using line numbers to avoid full file dumps in chat.
- **Shell-Level Interception:** Deterministic zsh wrappers block noisy native outputs (like verbose `git commit` messages) and return a concise status summary to the agent.
- **Two-Layer Git Memory:** Bypasses verbose `git log` commands. Uses `memory_search.sh` to query hashes via keywords first, then `memory_diff.sh` to display structural changes.

---

## 4. Workflow Integrations

### Transition to Eclipse Theia (VSCode Extension)
Instead of maintaining a custom Tauri shell from scratch, the project is pivoting to a VSCode/Theia extension architecture. This solves terminal keybinding and layout stability issues, while gaining access to:
- Native text decorators and virtual documents for a 100% text-driven, mouse-free Kanban board interface.
- Standard IDE editors, code lenses, terminal integration, and built-in markdown previews.

### Real-Time Data Fetching (WebFetch vs. WebSearch)
To prevent LLM hallucination of time-sensitive data (e.g. weather, stocks), agents bypass generic web search result summaries and fetch raw authoritative HTML pages (e.g., using `wttr.in`) to extract correct factual values.

### Workspace Identity Guardrails
Recognizing the user's role and learning habits, task structures are kept atomic, actionable, and shallow to maximize momentum. Notes are systematically routed to a central iCloud Obsidian vault using human-friendly names (e.g., `Topic 🚀.md`) rather than timestamp strings.
