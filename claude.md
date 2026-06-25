# Claude Profile & System Instructions

## Core Operating Rules
1. **Context Initialization:** Read `AG_CONTEXT.md` at the project root before starting any work. If missing, create it. Update it with durable knowledge (bullet points only) after significant architectural changes.
2. **Environment Restraints (Home Directory):** The home directory (`~`) is **never** a project root. Never initialize a git repository in `~` or its direct subdirectories.
3. **Safety First:** **Never** use `rm`. Always use `mv [path] ~/.Trash/` (Exception: `node_modules`).
4. **Tooling & Privacy:** Always use `pnpm`. Never use `npm`. All generated GitHub repositories must use the `--private` flag.
5. **Local Scoping:** Never use system-level `/tmp`. Always create and use a local `./tmp` folder within the current project directory for temporary files or test scripts to prevent permission errors.
6. **Token Protection & Builds:** Never run raw verbose compile/build commands (e.g., raw `xcodebuild`) that dump massive logs. Filter command outputs to print only the success status or relevant compiler error/warning highlights to protect the context window.
7. **Feature Documentation:** When implementing features or fixes, always document new capabilities by updating the features list in `FEATURES.md` at the project root.

---

## Environment & Paths
- **User Projects Root:** `/Users/matthewmurphy/projects/`
- **Active Core Project (ai-os):** `/Users/matthewmurphy/projects/ai-os`
- **Personal Notes (Obsidian iCloud):** `/Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`
- **Global Suggestions Config:** `~/.ai-os/suggestions.json`

---

## Project Detection
1. **Root Rule:** A "Project Root" is defined as the nearest ancestor containing a `.git` folder, `package.json`, `Cargo.toml`, `requirements.txt`, or `go.mod`.
2. **Fallback:** If no project root is found, default to the current working directory, provided it does not violate the Home Directory rule.

---

## Agent Work Logs & Session Continuity
Maintain a strict history of agentic attempts across sessions to preserve state.

1. **Log Directory:** Locate and maintain `.agent-logs/` at the project root.
2. **Fresh Thread Context:** When waking up in a fresh thread with insufficient context, always read the two most recent log files in `.agent-logs/` to piece together codebase state.
3. **Session Read:** Before starting a bug fix or feature, scan past logs to understand historical failures, architectural discoveries, and "What Didn't Work" to avoid repeating mistakes.
4. **Session Write:** At the end of every session involving code changes, create a new log file:
   - **Naming Convention:** `.agent-logs/YYYY-MM-DD_HH-MM_<short-kebab-description>.md`
   - **Required Sections:**
     - `## Goal`: Target objective.
     - `## Changes Made`: Files modified and why.
     - `## What Worked`: Confirmed fixes.
     - `## What Didn't Work / Known Issues`: Failed approaches and tech debt.
     - `## Architecture Notes`: Non-obvious codebase mechanics.

---

## Auto-Commit Protocol
- **Behavior:** Immediately following code changes and log creation, generate a concise, technical git commit message.
- **Execution:** Run `git add . && git commit -m "[message]"` autonomously.