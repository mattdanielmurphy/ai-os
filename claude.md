# Personal AI OS - Workspace Guardrails & Protocols

## 0. Global CLI Harness
Invoke the AI OS workspace via the registered global CLI:

```bash
ai-os [claude-args...]
```

The `ai-os` binary (registered via `pnpm link --global`) sets `$AI_OS_HOME` to `/Users/matthewmurphy/projects/ai-os` and invokes native `claude`. When run from `$HOME`, it automatically symlinks `/Users/matthewmurphy/projects/ai-os/CLAUDE.md` → `~/CLAUDE.md` if missing.

### 0.1 Home-Origin Execution Contract
This CLAUDE.md is symlinked into `~` as `~/CLAUDE.md` and is therefore the agent's first directive regardless of `cwd`. Execution loops may originate from `$HOME` before navigating down into specific project directories (e.g., `projects/CockBand`, `projects/StudyEngine`). The agent must:

* **Expect home-sourced launches:** Treat `~` as a valid entry point — do not reject execution from `$HOME`. The `ai-os` wrapper and the symlink chain ensure all absolute paths resolve correctly regardless of starting directory.
* **Resolve through the symlink:** When CLAUDE.md is read from `~/CLAUDE.md`, the effective project root is always `/Users/matthewmurphy/projects/ai-os` (the symlink target's canonical parent).
* **Route all scaffolding from the project root:** Even when launched from `~`, anchoring, scratch files, logs, and feature documentation must all resolve against `/Users/matthewmurphy/projects/ai-os/`.

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
* **Notes = Obsidian Vault (ALWAYS):** The word "notes" in any context (recent notes, show notes, save notes, find notes, etc.) refers exclusively to the Obsidian vault at:
    `/Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`
    It NEVER means agent logs, code comments, or any other directory. "Agent work logs" and "notes" are entirely separate concepts — never conflate them.
* **"Recent notes" Trigger:** When the user says "recent notes" (or equivalent), immediately run `ls -lt` on the Obsidian vault path above and present the latest files grouped by recency. Show filenames, modification dates, and a brief preview of content where practical.
* **Obsidian Injection (Save):** When told to "save" something to notes, bypass all other interpretations. Format as Markdown and write to:
    `/Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/<Human-Readable Title>.md`
    Use a descriptive, human-friendly filename derived from the content (e.g. `Space Facts 🚀.md`, `Recipe Ideas.md`, `Guitar Chords Notes.md`). NEVER use robotic timestamp-based names like `User_Note_YYYY-MM-DD_HHMMSS.md`. After saving, provide a clickable file link using an absolute `file://` URL so the user can open it directly.
* **Keyword Hijack Override (Native Memory Bypass):** When the user asks about "my notes", "personal notes", "saved notes", or equivalent phrasing, do NOT default to looking for a local `MEMORY.md` or native Claude Code project memory. You must explicitly bypass native memory interpretations and instead check the absolute Obsidian directory path:
    `/Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`
    If you need to list, read, or find notes, use the shell tool to run `ls` or query that specific iCloud Obsidian directory directly — never reference Claude's native `MEMORY.md` or session memory as the notes source.
* **Identity Matrix Override (Native Local Memory Override):** The workspace identity matrix at `/Users/matthewmurphy/projects/ai-os/MEMORY.md` and its `/Users/matthewmurphy/projects/ai-os/memory/` directory are the authoritative source for user identity, project context, and knowledge routing. These overrides native Claude Code file-based memory (`CLAUDE.md` local memory or session memory defaults). See `memory/claude-md-override.md` for the full precedence rules.

## 4. Execution & Interaction Hooks
* **Shell Input Deflection:** Escape exclamation points (`\!`) in all command strings to block shell history expansion errors.
* **Exploratory Investigations:** Default to temporal sorting via `ls -lt` or `ls -t` to pull relevant code files into view instantly.
* **Iteration Bounds:** Protect against runaway loops by adhering to these iteration caps based on query complexity:
    * Lite Tier: 3 Iterations
    * Flash Tier: 5 Iterations
    * Heavy Tier: 15 Iterations

## 5. The Agent Work Logs Protocol
* **Fresh Thread Ingestion:** At the start of a fresh session, immediately check the Obsidian vault at `/Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/` for recent session context. Sort by file modification date (`ls -lt`) or look for the strict glob pattern `User_Note_*.md` and read the most recent 2–3 files to reconstruct recent context and intentions.
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

## 7. Background Auto-Commit Protocol
* **Immediate Commit After Edits:** Immediately after modifying any files inside a git repository, and AFTER sending the user the text breakdown of the changes, you must immediately run a background git commit without waiting for further user instructions.
* **Commit Sequence:** The commit must be executed quietly with:
    `git add . && git commit -m "[Auto-Commit] [Brief technical summary of edits]"`
* **Visible Terminal Confirmation:** To ensure the user sees when the commit occurs, you must print a visible terminal confirmation line immediately following the execution, formatted exactly like this:
    `[ai-os] ✓ Changes successfully committed to background log.`