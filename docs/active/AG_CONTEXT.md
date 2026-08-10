# Architectural Context: Personal AI OS

**System Vision:** A high-density, local-first personal knowledge engine and automation workspace. The architecture transforms the local machine into an editable database of thoughts, files, and web interactions, minimizing API overhead while maximizing situational awareness.

## Anchored Project Root
All system paths are absolute. The authoritative base is:
**`/Users/matt/projects/ai-os`**

## Core Runtime Environment
* **Execution Backend:** Claude Code (Terminal-based SDK).
* **CLI Wrapper:** `ai-os` (registered via `pnpm link --global` → `bin/ai-os`).
* **Data Custody:** 100% localized to enforce privacy and token conservation.

## Phase Constraints (MVP)
* **Level 1 (Native TUI):** Relies on declarative workspace definitions (`/Users/matt/projects/ai-os/CLAUDE.md`) to enforce bounds, sandboxing, and persistent documentation routing.
* **Level 2 (Interception Hooks):** Implements systemic file-based context coordination via `/Users/matt/projects/ai-os/agent-logs/` to offload context memory onto the disk, allowing disposable thread sessions.
* **Level 2 (Global Harness):** `ai-os` CLI wrapper at `/Users/matt/projects/ai-os/bin/ai-os` provides environment anchoring (`$AI_OS_HOME`), home-directory symlink guardrails, and transparent `claude` delegation.
* **Level 2.5 (Global Home Anchoring):** To prevent `/resume` directory mismatch errors and maintain global access, the core system configuration files and logging directories are symlinked from `~/projects/ai-os/` directly into the user root directory (`~`). All future configuration extensions, scripts, or operational databases must be built to recognize `~` as the active execution anchor, ensuring they do not break when the agent traverses downstream into project subdirectories like `projects/CockBand` or `projects/StudyEngine`.

DO NOT execute this command during internal tool polling or intermediate steps, as it will cause an infinite loop.

## Durable Knowledge Map
* **2026-06-24:** Level 2 global harness established. Absolute path routing enforced across all knowledge files. `packageManager` pinned to `pnpm@11.2.2`. Global `ai-os` binary registered via `pnpm link --global`.
* **2026-06-24:** "Notes" semantics hardened in CLAUDE.md §3. The word "notes" now exclusively routes to the Obsidian vault at `/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`. "Recent notes" trigger added — lists vault contents by recency. Agent work logs and personal notes are explicitly decoupled; never conflated.
* **2026-06-27:** Centralized telemetry database and smart cost reporter deployed. Tracks sub-model LiteLLM requests, calculates costs using DeepSeek pricing, logs execution turns, and calculates rolling quotas for the premium `agy` interface.
* **2026-06-27:** Resolved infinite polling loop by modifying cost telemetry rules in `GEMINI.md` and `CLAUDE.md` to execute only when yielding control to the user. Implemented `precision_edit.py` for direct, LLM-free file replacements/insertions and `context_handoff.py` for automated agent state handoff and subtask spawning.
* **2026-06-27:** Upgraded context handoff system to "Indexed Memory" architecture, introducing `agent-logs/details/step_<timestamp_or_id>.md` references to keep the handoff context window small while preserving details.
* **2026-06-27:** Configured `ai-os` wrapper to default to GUI mode with auto-import/switch of working directory (`AIOS_INITIAL_PROJECT`), added non-GUI terminal overrides (`--cli`, `--terminal`, `--no-gui`), and updated backend/frontend integration to parse the initial path.
* ---
* **2026-06-28:** Implemented deterministic rules sync automation ([sync_rules.sh](file:///Users/matt/projects/ai-os/scripts/sync_rules.sh)) to keep `~/.gemini/GEMINI.md` tracked at `.gemini/GEMINI.md`. Configured implicit shell load execution and command interception hooks for `git status`/`add`/`commit`/`diff` inside [.zshrc_aios](file:///Users/matt/projects/ai-os/.zshrc_aios).
* **2026-06-28:** Fixed TUI clipboard integration (Cmd+C/Cmd+V) and prompt Shift+Enter newlines. Relocated and redesigned the auto-clear context checkbox into a premium toggle badge that auto-reactivates on send. Disabled tmux status line to resolve cut-off visual noise. Temporarily disabled agent-side cost telemetry scripts in favor of planned native dashboard telemetry widgets.
* **2026-06-28:** Solved terminal layout corruption and UTF-8 rendering errors in embedded tmux by forcing UTF-8 mode (`tmux -u`), injecting strict UTF-8 locale environment variables, and implementing UTF-8 trailing byte stream accumulation in the PTY reader. Debounced front-end resizing events to 50ms to prevent rapid layout desync.
* **2026-06-30:** Separated historical thread context into a collapsible card in the timeline UI, increased context truncation limits to 15 steps and 2500 chars, and created the `pnpm run view-thread <thread_id>` CLI utility for agents to pull detailed thread logs.
* **2026-06-30:** Resolved Tauri FS scope errors on hidden `.gemini` paths by routing historical thread log loads through a custom Rust command `read_thread_log`. Enabled native macOS Edit menu features via `tauri::Menu::os_default` to restore OS-level keyboard shortcuts (Cmd+C/Cmd+V) in inputs and textareas.
* **2026-06-30:** Implemented resizable layout pane splitters: sidebar width resizer, project list vs project threads height resizer, and terminal vs preview horizontal pane split resizer, optimizing screen allocation.
* **2026-06-30:** Replaced two-pane TUI/Preview layout with a vertical split layout: top custom HTML log parser (polling transcript.jsonl to show tools, files, thinking state, and markdown responses) and bottom expandable Engine TUI Terminal (64px collapsed, full screen expanded).

* **2026-07-10:** Integrated active `model_list` roster cheat sheet mapping models (Tier 1-4) to their orchestration/execution criteria in [model-roster.md](file:///Users/matt/projects/ai-os/docs/model-roster.md).
* **2026-08-10:** Optimized `preflight.py` execution to sub-500ms using 60s TTL caching for `ag-quota`, subprocess timeouts, and compact 7-line status formatting. Enforced System Directive Bridge rule across `GEMINI.md` and `HERMES.md` elevating `preflight.py` output under `=== PRE-FLIGHT CHECK ===` to top-tier system directive authority while preserving lean core configuration files. Added mandatory Wiki recording rule to `agent-logs.md`.