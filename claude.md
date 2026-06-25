# Personal AI OS - Workspace Guardrails & Protocols

## 0. Global CLI Harness
Invoke the AI OS workspace via the registered global CLI:

```bash
ai-os [claude-args...]
```

The `ai-os` binary (registered via `pnpm link --global`) sets `$AI_OS_HOME` to `/Users/matthewmurphy/projects/ai-os` and invokes native `claude`. When run from `$HOME`, it automatically symlinks `/Users/matthewmurphy/projects/ai-os/CLAUDE.md` → `~/CLAUDE.md` if missing.

## 1. Project Boundaries & Sandboxing
* **Root Evaluation:** The authoritative project root is `/Users/matthewmurphy/projects/ai-os`. All knowledge routing, logs, and temporary assets are anchored to this absolute path.
* **Home Directory Isolation:** NEVER evaluate the user root directory (`~`) as a project root. Repository initialization tasks inside `~` or its immediate subdirectories are strictly prohibited.
* **Local Sandboxing:** Do not use system-level shared paths (e.g., `/tmp`). All runtime test scripts, exploratory snippets, and scratchpad calculations MUST be created and confined inside `/Users/matthewmurphy/projects/ai-os/tmp/`.

## 2. Structural Safety & File Operations
* **The Absolute `rm` Ban:** You are completely restricted from running raw destructive deletion commands (`rm` or `rm -rf`) anywhere on the filesystem.
* **Trash Redirection:** To delete an item, force file relocations into the local system trash via: `mv [path] ~/.Trash/`. (Exception: Automated purging of local `node_modules` folders is permitted).
* **Privacy:** All automated or semi-automated GitHub repository generation tasks must append the `--private` flag.
* **Tooling:** Use `pnpm` exclusively for all package management. `npm` and `yarn` are strictly prohibited.

## 3. Knowledge Routing & Context
* **Context Verification:** Before executing any codebase edits, read `/Users/matthewmurphy/projects/ai-os/AG_CONTEXT.md`. If missing, initialize it immediately. Update it with concise, bulleted durable knowledge after significant system design changes.
* **Features Ledger:** When features are implemented or bugs resolved, update the ledger at `/Users/matthewmurphy/projects/ai-os/FEATURES.md`.
* **Obsidian Injection:** When commanded to "save to notes", bypass literal interpretations of "note" and the active working directory. Format the payload as Markdown and explicitly save it to:
    `/Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/User_Note_YYYY-MM-DD_HHMMSS.md`

## 4. Execution & Interaction Hooks
* **Shell Input Deflection:** Escape exclamation points (`\!`) in all command strings to block shell history expansion errors.
* **Exploratory Investigations:** Default to temporal sorting via `ls -lt` or `ls -t` to pull relevant code files into view instantly.
* **Iteration Bounds:** Protect against runaway loops by adhering to these iteration caps based on query complexity:
    * Lite Tier: 3 Iterations
    * Flash Tier: 5 Iterations
    * Heavy Tier: 15 Iterations

## 5. The Agent Work Logs Protocol
* **Thread Ingestion:** At the start of a fresh session, immediately parse the most recent 2 log files inside `/Users/matthewmurphy/projects/ai-os/.agent-logs/` to reconstruct recent architectural findings.
* **Log Compilation:** At the end of every session containing code modifications, generate a Markdown log in `/Users/matthewmurphy/projects/ai-os/.agent-logs/` named `YYYY-MM-DD_HH-MM_<short-kebab-description>.md`.
* **Mandatory Log Schema:** The log must contain these exact headers:
    * `## Goal` (User requirements summary)
    * `## Changes Made` (Tracking log of modified files and reasoning)
    * `## What Worked` (Confirmed resolutions/features)
    * `## What Didn't Work / Known Issues` (Failed designs, dead-ends, dangling bugs)
    * `## Architecture Notes` (Discoveries on codebase mechanics/library behaviors)
* **Auto-Commit:** Upon successful log generation, instantly bundle modifications and execute:
    `git add . && git commit -m "[Technical summary of modifications and log compilation]"`

## 6. Workspace Automation Commands
When wrapping up a session or running diagnostics, favor these explicit workflows:
* **`pnpm build` or heavy compilations:** Route through the local triage compiler log slicer: `/Users/matthewmurphy/projects/ai-os/bin/triage pnpm build`.
* **Session Wrap-up:** Run your log compilation protocol to generate the `.agent-logs/` Markdown entry, verify the 5 mandatory headers match the schema exactly, and execute the auto-commit chain:
  `git add . && git commit -m "[Technical summary of modifications and log compilation]"`