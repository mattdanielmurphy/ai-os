# Architectural Context: Personal AI OS

**System Vision:** A high-density, local-first personal knowledge engine and automation workspace. The architecture transforms the local machine into an editable database of thoughts, files, and web interactions, minimizing API overhead while maximizing situational awareness.

## Anchored Project Root
All system paths are absolute. The authoritative base is:
**`/Users/matthewmurphy/projects/ai-os`**

## Core Runtime Environment
* **Execution Backend:** Claude Code (Terminal-based SDK).
* **CLI Wrapper:** `ai-os` (registered via `pnpm link --global` → `bin/ai-os`).
* **Data Custody:** 100% localized to enforce privacy and token conservation.

## Phase Constraints (MVP)
* **Level 1 (Native TUI):** Relies on declarative workspace definitions (`/Users/matthewmurphy/projects/ai-os/CLAUDE.md`) to enforce bounds, sandboxing, and persistent documentation routing.
* **Level 2 (Interception Hooks):** Implements systemic file-based context coordination via `/Users/matthewmurphy/projects/ai-os/.agent-logs/` to offload context memory onto the disk, allowing disposable thread sessions.
* **Level 2 (Global Harness):** `ai-os` CLI wrapper at `/Users/matthewmurphy/projects/ai-os/bin/ai-os` provides environment anchoring (`$AI_OS_HOME`), home-directory symlink guardrails, and transparent `claude` delegation.
* **Level 2.5 (Global Home Anchoring):** To prevent `/resume` directory mismatch errors and maintain global access, the core system configuration files and logging directories are symlinked from `~/projects/ai-os/` directly into the user root directory (`~`). All future configuration extensions, scripts, or operational databases must be built to recognize `~` as the active execution anchor, ensuring they do not break when the agent traverses downstream into project subdirectories like `projects/CockBand` or `projects/StudyEngine`.

## Durable Knowledge Map
* **2026-06-24:** Level 2 global harness established. Absolute path routing enforced across all knowledge files. `packageManager` pinned to `pnpm@11.2.2`. Global `ai-os` binary registered via `pnpm link --global`.
* **2026-06-24:** "Notes" semantics hardened in CLAUDE.md §3. The word "notes" now exclusively routes to the Obsidian vault at `/Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`. "Recent notes" trigger added — lists vault contents by recency. Agent work logs and personal notes are explicitly decoupled; never conflated.