---
title: "Organize Global Agent Configuration"
date: "2026-07-20"
conversation_id: "28f2a00e-1450-4b46-8e18-c0682f93199e"
source: "antigravity"
---

# Organize Global Agent Configuration

## User

SYSTEM: You are Hermes Agent, the primary high-level reasoning engine for Matt's local AI orchestration system. You operate as the daily-driver architect and executor alongside `agy` (a separate, cheaper worker-bee CLI that lives in `~/projects/ai-os`). You and agy are parallel systems — you do not share context files, but you may call agy's scripts as subagents when beneficial.

## Who You Work For

Matt is a CS student and drummer. He self-studies calculus, tends to procrastinate, and responds best to atomic, immediately-actionable tasks.

### Active Projects
- **ai-os** (`~/projects/ai-os`) — Local-first AI harness (Tauri + Rust + Gemini integration)
- **CockBand** — Drum/bass Rocksmith-style clone
- **StudyEngine** — PencilKit/LaTeX note-taking app
- **Piano OS** — Tauri/Rust MIDI platform

## Absolute Knowledge Routing

These routing rules are non-negotiable and override any other memory or context:

- **"Notes", "personal notes", "my notes", "saved notes"** → Route EXCLUSIVELY to the iCloud Obsidian vault at:
  `/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`
  Use the Obsidian skill (load with `skill_view(name='obsidian')`) for reading/writing vault content. When creating notes, use human-readable filenames (e.g., `Space Facts 🚀.md`) and provide clickable `file://` links.

- **Session engineering logs** → Write to the relevant project's `agent-logs/` directory. For ai-os specifically: `/Users/matt/projects/ai-os/agent-logs/`

## Hard Constraints

1. **Package manager:** `pnpm` exclusively. Never use `npm` or `yarn`.
2. **Safety:** Never use `rm`. Use `mv [path] ~/.Trash/` instead.
3. **Privacy:** All generated GitHub repos must use `--private`.
4. **No repo in ~:** Never initialize a git repository in the home directory.
5. **Local temp:** Use `./tmp` within the project directory, never `/tmp`.
6. **Username guardrail:** The host migrated from `matthewmurphy` to `matt`. Translate any `/Users/matthewmurphy/` paths to `/Users/matt/`. The old userna
<truncated 42046 bytes>
══════
USER PROFILE (who the user is) [65% — 895/1,375 chars]
══════════════════════════════════════════════
When the Hermes Studio dev server shows ECONNREFUSED on 8642, assume the gateway IS running and the API server just needs enabling — do not dismiss it as "expected for frontend-only dev." The gateway API must be fully connected for Studio to work properly.
§
Prefers thorough verification before assuming a service isn't running. Corrected me when I said "ECONNREFUSED is expected — the gateway isn't running on this machine" — it was, just missing config. Wants me to dig deeper and check the actual state before concluding.
§
Prefers surgical, precisely-scoped changes when migrating architecture — 'replace only the component that needs replacing, leave everything else untouched'. When I proposed replacing the whole PTY/tmux/xterm approach, they corrected: 'only for Hermes, keep agy and Claude on xterm.js'. Apply this precision-scoping default to any future migration or refactoring task.

Conversation started: Monday, July 20, 2026
Model: agy
Provider: custom

USER: Something I need you to clear up: We have a local files: GEMINI.md, CLAUDE.md, AGENTS.md.
First of all, why all three?
Secondly, these are supposed to be GLOBALLY accessible... meaning, GEMINI.md should be at ~/.gemini/GEMINI.md and nowhere else.
Unless it's just like rsycned here so it can be part of the repo (which it should be).
I believe we set up an rsync system.
Make this whole thing clear and organized and robust for me please.

---

## Assistant

Created At: 2026-07-20T01:32:26-06:00
Completed At: 2026-07-20T01:32:27-06:00

				The command completed successfully.
				Output:
				<truncated 113 lines>
	agent-logs/2026-06-30_17-20_fix-project-sidebar-fragmentation-and-thread-association.md
	agent-logs/2026-06-30_17-22_sanitize-project-paths.md
	agent-logs/2026-06-30_17-23_group-uncategorized-threads-misc.md
	agent-logs/2026-06-30_17-39_constrain-markdown-line-length.md
	agent-logs/2026-06-30_17-45_separate-historical-context-and-view-thread.md
	agent-logs/2026-06-30_17-50_consolidate-continued-threads.md
	agent-logs/2026-06-30_17-52_fix-sidebar-flicker-and-sorting.md
	agent-logs/2026-06-30_18-06_thread-caching-and-typing-performance.md
	agent-logs/2026-06-30_21-48-fix-prod-terminal.md
	agent-logs/2026-06-30_21-57_fix-production-tmux-connection.md
	agent-logs/2026-06-30_22-01_fix-thread-ui-lag.md
	agent-logs/2026-06-30_22-04_thread-deletion-and-placeholder-fix.md
	agent-logs/2026-07-01_01-26_add-cmd-n-new-thread-shortcut.md
	agent-logs/2026-07-01_01-32_fix-thread-delete-btn-and-multiple-blank-threads.md
	agent-logs/2026-07-01_01-58-preserve-details-state.md
	agent-logs/2026-07-01_02-19_resume-leaf-thread.md
	agent-logs/2026-07-01_02-23_add-copy-buttons.md
	agent-logs/2026-07-01_02-42-quota-display-current-account.md
	agent-logs/2026-07-01_02-51_get-quota-cli-log.md
	agent-logs/2026-07-01_02-58_fix-quota-log-dir.md
	agent-logs/2026-07-02_19-53_add-browser-context-tauri-command.md
	agent-logs/2026-07-02_19-59_fix-main-preview-stuck.md
	agent-logs/2026-07-02_20-03_fix-auto-clear-context-bypass.md
	agent-logs/2026-07-02_20-06-floating-window-setup.md
	agent-logs/2026-07-02_20-09-floating-window-frontend.md
	agent-logs/2026-07-02_20-10-gemini-dispatch.md
	agent-logs/2026-07-02_20-19-simplify-floating-window.md
	agent-logs/2026-07-02_20-26_fix-xterm-hidden-write-crash.md
	agent-logs/2026-07-02_20-46-floating-gemini-compressed.md
	agent-logs/2026-07-02_21-10-fix-floating-window-js.md
	agent-logs/2026-07-02_21-37_transparent-floating-gemini-window.md
	agent-logs/202
<truncated 4213 bytes>
09_16-26_Support automatic transcript discovery in audit_transcripts.py.md
	agent-logs/2026-07-09_16-30_update gather-context clipboard behavior in package.json.md
	agent-logs/2026-07-09_16-55_implement-architecture-and-optimization-changes.md
	agent-logs/2026-07-09_17-46_migrate-macos-text-replacements-and-compare.md
	agent-logs/2026-07-09_17-55_fix-kanban-task-management.md
	agent-logs/2026-07-09_18-22_optimize-gemini-userscript.md
	agent-logs/2026-07-09_18-31_improve transcript token auditing.md
	agent-logs/2026-07-09_21-21_eliminate-quota-waste.md
	agent-logs/2026-07-09_21-23_improve-transcript-token-auditing.md
	agent-logs/2026-07-09_21-31_seal-token-leaks-and-delegation.md
	agent-logs/2026-07-10_01-41_monitor-litellm-launch-agent.md
	agent-logs/2026-07-10_11-03_fix-gemini-md-disappearing.md
	agent-logs/2026-07-10_11-12_fix-raycast-migration-permissions.md
	agent-logs/2026-07-10_11-33_universal-agent-framework.md
	agent-logs/2026-07-10_11-51_add active model roster cheat sheet to docs.md
	agent-logs/2026-07-10_12-03_implement three-turn delegation protocol.md
	agent-logs/2026-07-10_12-04_token-waste-audit.md
	agent-logs/2026-07-10_12-07_limit-context-bloat-rules.md
	agent-logs/2026-07-10_12-28_token-waste-fixes.md
	agent-logs/2026-07-10_12-32_token-waste-fixes.md
	agent-logs/2026-07-10_16-45_tmux-agent-wrapper-migration.md
	agent-logs/2026-07-10_16-49_gemini-archive-ingestion-agent.md
	agent-logs/2026-07-10_19-37_sync-hermes-threads.md
	agent-logs/2026-07-10_19-45_sync-hermes-threads-both-brains.md
	agent-logs/2026-07-11_16-13_agy-mcp-install-and-docs.md
	agent-logs/2026-07-11_16-23_integrate-agy-mcp-into-hermes.md
	agent-logs/2026-07-13_10-15_account-migration-music-password-fix.md
	agent-logs/2026-07-15_22-26_apple-passwords-extension-troubleshooting.md
	agent-logs/2026-07-16_03-35_agy-ping-cronjob.md
	agent-logs/2026-07-19_16-48_reorganization-and-glic-plan.md
	agent-logs/2026-07-20_00-30_strategic-pivot-minimal-fork-triage.md
	services/

no changes added to commit (use "git add" and/or "git commit -a")

Created At: 2026-07-20T01:32:28-06:00
Completed At: 2026-07-20T01:32:28-06:00

				The command completed successfully.
				Output:
				./DEVELOPMENT_JOURNAL.md
./todo.md
./README.md
./FEATURES.md
./AGENTS.md
./AG_CONTEXT.md
./CLAUDE.md

Created At: 2026-07-20T01:32:30-06:00
Completed At: 2026-07-20T01:32:30-06:00

				The command completed successfully.
				Output:
				total 144
drwxr-xr-x@ 25 matt  staff    800 Jul 20 01:31 .
drwxr-x---+ 90 matt  staff   2880 Jul 20 01:27 ..
-rw-r--r--@  1 matt  staff  14340 Jul 19 23:44 .DS_Store
-rw-r--r--@  1 matt  staff   9102 Jul 11 21:07 GEMINI.md
drwxr-xr-x@ 19 matt  staff    608 Jul 20 00:27 antigravity
drwxr-xr-x@ 10 matt  staff    320 Jul  6 21:43 antigravity-backup
drwxr-xr-x  27 matt  staff    864 Jul 20 01:32 antigravity-cli
drwxr-xr-x@ 16 matt  staff    512 Jul 10 12:23 antigravity-ide
drwxr-xr-x@ 11 matt  staff    352 Jul 19 23:40 config
-rw-------@  1 matt  staff    294 Jul  6 21:43 extension_integrity.json
drwxr-xr-x@  4 matt  staff    128 Jun 12 18:59 extensions
-rw-r--r--@  1 matt  staff    195 Jul 20 01:31 google_accounts.json
-rw-r--r--@  1 matt  staff    195 Jul 20 01:31 google_accounts.json.bak
drwxr-xr-x@ 22 matt  staff    704 Jul 19 16:42 history
-rw-r--r--@  1 matt  staff     36 Jul  6 21:43 installation_id
-rw-r--r--@  1 matt  staff   1572 Jul 20 01:31 oauth_creds.json
-rw-r--r--@  1 matt  staff   1572 Jul 20 01:31 oauth_creds.json.bak
-rw-r--r--@  1 matt  staff   1154 Jul 19 16:42 projects.json
drwxr-xr-x   3 matt  staff     96 Jul  6 10:57 rules
drwxr-xr-x   2 matt  staff     64 Jun 25 03:30 sessions
-rw-r--r--@  1 matt  staff    224 Jul 20 01:31 settings.json
-rw-r--r--@  1 matt  staff    224 Jul 20 01:31 settings.json.bak
-rw-r--r--   1 matt  staff    356 Jul  6 21:44 state.json
drwxr-xr-x@ 24 matt  staff    768 Jul 19 16:42 tmp
-rw-------   1 matt  staff    186 Jul  6 21:44 trustedFolders.json

Created At: 2026-07-20T01:32:31-06:00
Completed At: 2026-07-20T01:32:31-06:00

				The command completed successfully.
				Output:
				a1ed483 [Auto-Commit] Rename and restructure GEMINI.md to AGENTS.md with updated project protocols and rules
13c6283 [Auto-Commit] Add agent log documenting fix for disappearing GEMINI.md rules file
c71a54a Refine editing exception clause for small files/known edit points in GEMINI.md
4a95cf2 Detail task delegation and quota conservation rules in GEMINI.md
eeea526 Add Telemetry Prohibitions rule to GEMINI.md
eccf78f Refactor GEMINI.md system prompts into dynamic triage vs worker bee modes
3aa85aa docs(agents): restore GEMINI.md symlink
ffe12bf Add agent work log for GEMINI.md updates
25054f4 [Auto-Commit] Implement Two-Layer Git Memory tools and inject system rules to GEMINI.md

Created At: 2026-07-20T01:32:32-06:00
Completed At: 2026-07-20T01:32:32-06:00
File Path: `file:///Users/matt/projects/ai-os/agent-logs/2026-07-10_11-03_fix-gemini-md-disappearing.md`
Total Lines: 23
Total Bytes: 1434
Showing lines 1 to 23
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: [Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-ide/brain/4c029b2f-e424-4e9b-b563-1ec578e6d0b2/.system_generated/logs/transcript.jsonl)
2: 
3: ## Goal
4: Identify why the global `GEMINI.md` rules file keeps disappearing/getting deleted and prevent it from recurring.
5: 
6: ## Changes Made
7: - Restored `~/.gemini/GEMINI.md` from the backup at `~/.gemini/GEMINI.bak`.
8: - Added a safety check to `scripts/sync_rules.sh` to skip rsync if the source rules file `~/.gemini/GEMINI.md` is empty/0 bytes but the target file `.gemini/GEMINI.md` exists and is not empty.
9: - Created `.devtool/features/fix-gemini-md-disappearing.md` tracking the bug fix and transitioned it to `status: "review"`.
10: 
11: ## What Worked
12: - Restoring `~/.gemini/GEMINI.md` from `GEMINI.bak` successfully brought back the rules.
13: - The `git status` hook and watcher automatically synced the restored rules back to the workspace.
14: - The safety check prevents silent overwriting of non-empty workspace rules files with blank files in the future.
15: 
16: ## What Didn't Work / Known Issues
17: None.
18: 
19: ## Architecture Notes
20: - The shell environment intercepts git commands and terminal startups to run `scripts/sync_rules.sh`, which performs a one-way rsync from `~/.gemini/GEMINI.md` to `.gemini/GEMINI.md`.
21: 
22: [Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-ide/brain/4c029b2f-e424-4e9b-b563-1ec578e6d0b2/.system_generated/logs/transcript.jsonl)
23: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-20T01:32:33-06:00
Completed At: 2026-07-20T01:32:34-06:00

				The command completed successfully.
				Output:
				<truncated 9 lines>
./node_modules/.old_modules-42bb52baed4d906c/.old_tauri-gui_modules/.pnpm/typescript@5.9.3/node_modules/typescript/lib/lib.dom.asynciterable.d.ts
./node_modules/.old_modules-42bb52baed4d906c/.old_tauri-gui_modules/.pnpm/typescript@5.9.3/node_modules/typescript/lib/lib.es2018.asynciterable.d.ts
./node_modules/.old_modules-42bb52baed4d906c/.old_tauri-gui_modules/.pnpm/typescript@5.9.3/node_modules/typescript/lib/lib.webworker.asynciterable.d.ts
./node_modules/.old_modules-42bb52baed4d906c/.old_tauri-gui_modules/.pnpm/typescript@5.9.3/node_modules/typescript/lib/lib.es2018.asyncgenerator.d.ts
./node_modules/.old_modules-42bb52baed4d906c/.old_tauri-gui_modules/.pnpm/@xterm+xterm@6.0.0/node_modules/@xterm/xterm/src/vs/base/common/async.ts
./node_modules/.bun/nanoid@3.3.16/node_modules/nanoid/async
./node_modules/.bun/@types+node@24.13.3/node_modules/@types/node/async_hooks.d.ts
./node_modules/.bun/typescript@5.9.3/node_modules/typescript/lib/lib.dom.asynciterable.d.ts
./node_modules/.bun/typescript@5.9.3/node_modules/typescript/lib/lib.es2018.asynciterable.d.ts
./node_modules/.bun/typescript@5.9.3/node_modules/typescript/lib/lib.webworker.asynciterable.d.ts
./node_modules/.bun/typescript@5.9.3/node_modules/typescript/lib/lib.es2018.asyncgenerator.d.ts
./node_modules/.bun/@xterm+xterm@6.0.0/node_modules/@xterm/xterm/src/vs/base/common/async.ts
./thread-browser/frontend/node_modules/type-fest/source/async-return-type.d.ts
./thread-browser/frontend/node_modules/type-fest/source/asyncify.d.ts
./thread-browser/frontend/node_modules/escalade/sync
./thread-browser/frontend/node_modules/nanoid/async
./thread-browser/frontend/node_modules/gensync
./thread-browser/frontend/node_modules/typescript/lib/lib.dom.asynciterable.d.ts
./thread-browser/frontend/node_modules/typescript/lib/lib.es2018.asynciterable.d.ts
./thread-browser/frontend/node_modules/typescript/lib/lib.webworker
<truncated 4219 bytes>
uri/target/debug/.fingerprint/sync_wrapper-a3e9fb0a4281149d/lib-sync_wrapper.json
./tauri-gui/src-tauri/target/debug/.fingerprint/sync_wrapper-a3e9fb0a4281149d/dep-lib-sync_wrapper
./tauri-gui/src-tauri/target/debug/.fingerprint/sync_wrapper-1774d746f256cbcf
./tauri-gui/src-tauri/target/debug/.fingerprint/sync_wrapper-1774d746f256cbcf/lib-sync_wrapper
./tauri-gui/src-tauri/target/debug/.fingerprint/sync_wrapper-1774d746f256cbcf/lib-sync_wrapper.json
./tauri-gui/src-tauri/target/debug/.fingerprint/sync_wrapper-1774d746f256cbcf/dep-lib-sync_wrapper
./tauri-gui/src-tauri/target/debug/deps/libsync_wrapper-a3e9fb0a4281149d.rmeta
./tauri-gui/src-tauri/target/debug/deps/sync_wrapper-a3e9fb0a4281149d.d
./tauri-gui/src-tauri/target/debug/deps/sync_wrapper-1774d746f256cbcf.d
./tauri-gui/src-tauri/target/debug/deps/libsync_wrapper-1774d746f256cbcf.rmeta
./tauri-gui/src-tauri/target/debug/deps/sync_wrapper-1774d746f256cbcf.sync_wrapper.a97ea8bf5ae4acd4-cgu.0.rcgu.o
./tauri-gui/src-tauri/target/debug/deps/libsync_wrapper-1774d746f256cbcf.rlib
./tauri-gui/src-tauri/target/debug/build/html5ever-89660581e0672f95/out/rules.rs
./scripts/sync_threads.py
./scripts/sync_rules.sh
./.agy-mcp/worktrees/job-7f1a74efbfca4784/agent-logs/2026-07-18_17-42_update-handoff-rules.md
./.agy-mcp/worktrees/job-7f1a74efbfca4784/scripts/sync_threads.py
./.agy-mcp/worktrees/job-7f1a74efbfca4784/scripts/sync_rules.sh
./.agy-mcp/worktrees/job-7f1a74efbfca4784/.devtool/features/archive/legacy-tauri-gui/kanban-todo-sync.md
./.agy-mcp/worktrees/job-7f1a74efbfca4784/.devtool/features/archived/limit-context-bloat-rules.md
./.agy-mcp/worktrees/job-7f1a74efbfca4784/.devtool/features/archived/sync-hermes-threads.md
./.agy-mcp/worktrees/job-7f1a74efbfca4784/.devtool/features/archived/sync-rules-to-gemini-md.md
./.devtool/features/archive/legacy-tauri-gui/kanban-todo-sync.md
./.devtool/features/archived/limit-context-bloat-rules.md
./.devtool/features/archived/sync-hermes-threads.md
./.devtool/features/archived/sync-rules-to-gemini-md.md
./tmp/rules_watcher.log

Created At: 2026-07-20T01:32:36-06:00
Completed At: 2026-07-20T01:32:36-06:00
File Path: `file:///Users/matt/projects/ai-os/scripts/sync_rules.sh`
Total Lines: 29
Total Bytes: 901
Showing lines 1 to 29
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: #!/bin/bash
2: # Sync system rules file to the active project repository
3: 
4: set -euo pipefail
5: 
6: SOURCE_FILE="$HOME/.gemini/GEMINI.md"
7: TARGET_DIR=".gemini"
8: TARGET_FILE="$TARGET_DIR/GEMINI.md"
9: 
10: # Safety check: ensure source file exists and is not empty
11: if [ ! -f "$SOURCE_FILE" ]; then
12:     echo "❌ Error: Source file not found at $SOURCE_FILE" >&2
13:     exit 1
14: fi
15: 
16: # Safety check: if target exists and is not empty, but source is empty, print warning and exit 0
17: if [ -s "$TARGET_FILE" ] && [ ! -s "$SOURCE_FILE" ]; then
18:     echo "⚠️ Warning: Target file $TARGET_FILE exists and is not empty, but source file $SOURCE_FILE is empty. Skipping rsync." >&2
19:     exit 0
20: fi
21: 
22: # Ensure target directory exists in workspace
23: mkdir -p "$TARGET_DIR"
24: 
25: # Run rsync to sync files deterministically
26: rsync -av "$SOURCE_FILE" "$TARGET_FILE"
27: 
28: echo "✅ Rules synced successfully from ~/.gemini/GEMINI.md to .gemini/GEMINI.md"
29: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-20T01:32:37-06:00
Completed At: 2026-07-20T01:32:37-06:00
File Path: `file:///Users/matt/projects/ai-os/AGENTS.md`
Total Lines: 114
Total Bytes: 17704
Showing lines 1 to 114
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Core Project Rules
2: 
3: ## Auto-Commit Protocol
4: **Commit:** Run `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` to delegate the commit process to a cheaper subagent/script.
5: 
6: ## Project Detection
7: 1. **Root Rule:** A "Project Root" is the nearest ancestor containing a `.git` folder, `package.json`, `Cargo.toml`, `requirements.txt`, or `go.mod`.
8: 2. **Exception:** The home directory (`~`) is NOT a project root, even if it contains these files.
9: 3. **Hierarchy:** If no project root is found, default to the current working directory, but NEVER initialize a git repository in `~` or its subdirectories (unless it's a known project folder in `~/projects/`).
10: 
11: ## Core Rules
12: 1. **Context:** Read `AG_CONTEXT.md` at the project root before ANY work. If missing, create it at the root. Update it with durable knowledge (bullets only) after significant architectural changes.
13: 2. **Safety:** NEVER use `rm`. ALWAYS use `mv [path] ~/.Trash/` (Exception: `node_modules`).
14: 3. **Tooling:** ALWAYS use `bun`. NEVER use `npm` or `pnpm`. If you start work on an existing project that uses npm, pnpm, or yarn, you MUST migrate it to Bun first (delete node_modules and old lockfiles, run `bun install`, and update package.json scripts) before starting your main task.
15: 4. **Privacy:** ALL generated GitHub repos MUST use `--private`.
16: 5. **No Repo in ~:** NEVER initialize a git repository in the home directory (`~`).
17: 6. **Local Temp:** NEVER use system-level `/tmp`. ALWAYS create and use a `./tmp` folder within the current project directory for temporary file
<truncated 14589 bytes>
he `handover.py` script, which replaces the current process (`os.execvp("agy", ...)`) to attach the interactive `agy` CLI session directly to your terminal. Execute the handoff by running:
100:   `python3 /Users/matt/projects/ai-os/scripts/handover.py --to-model pro --completed "<what you analyzed/researched>" --next-steps "<what needs to be done next>"`
101: - **Exclusively Use agy for Subagents**: When agy quota is high/abundant, use agy exclusively. If a prompt goes to Hermes (default), use the MCP tool to spawn a tmux-bound `agy` CLI instance as a subagent, or if already in agy, have agy spin up its own subagent natively. Do not spawn external API agents or run subagents without attaching/steering capabilities.
102: 
103: # Global Workflows
104: @~/.ai-workflows/audit.md
105: @~/.ai-workflows/fast.md
106: @~/.ai-workflows/start.md
107: 
108: ## Chrome DevTools MCP Safety Rules
109: The user runs a single Chrome instance with the remote debugging port open, meaning their personal browsing tabs are mixed with development tabs. To protect the user's personal data and workflow, you MUST strictly adhere to the following rules when using Chrome DevTools MCP:
110: 
111: 1. **Verify the Target Tab**: Before taking any action (navigating, clicking, typing, evaluating script), ALWAYS use `mcp_chrome-devtools_list_pages` to get the list of open tabs and their IDs.
112: 2. **Require Confirmation on Ambiguity**: If it is not 100% obvious which tab you are supposed to interact with, you MUST ask the user to confirm the target tab before doing anything. 
113: 3. **Strict Isolation**: NEVER modify, close, navigate, or clear data on any tab other than the explicit target tab. Treat all other tabs as off-limits personal data.
114: 4. **Prefer New Tabs**: If a task requires testing a new URL or running a clean test, use `mcp_chrome-devtools_new_page` to spawn a fresh tab rather than hijacking an existing one. Work exclusively within that new tab.
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-20T01:32:38-06:00
Completed At: 2026-07-20T01:32:38-06:00
File Path: `file:///Users/matt/projects/ai-os/CLAUDE.md`
Total Lines: 116
Total Bytes: 15841
Showing lines 1 to 116
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: <SYSTEM_INSTRUCTIONS>
2: <AUTO_COMMIT_PROTOCOL>
3: **Commit:** Run `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` to delegate the commit process to a cheaper subagent/script.
4: </AUTO_COMMIT_PROTOCOL>
5: 
6: <PROJECT_DETECTION>
7: 1. **Root Rule:** A "Project Root" is the nearest ancestor containing a `.git` folder, `package.json`, `Cargo.toml`, `requirements.txt`, or `go.mod`.
8: 2. **Exception:** The home directory (`~`) is NOT a project root, even if it contains these files.
9: 3. **Hierarchy:** If no project root is found, default to the current working directory, but NEVER initialize a git repository in `~` or its subdirectories (unless it's a known project folder in `~/projects/`).
10: </PROJECT_DETECTION>
11: 
12: <CORE_RULES>
13: 1. **Context:** Read `AG_CONTEXT.md` at the project root before ANY work. If missing, create it at the root. Update it with durable knowledge (bullets only) after significant architectural changes.
14: 2. **Safety:** NEVER use `rm`. ALWAYS use `mv [path] ~/.Trash/` (Exception: `node_modules`).
15: 3. **Tooling:** ALWAYS use `bun`. NEVER use `npm` or `pnpm`. If you start work on an existing project that uses npm, pnpm, or yarn, you MUST migrate it to Bun first (delete node_modules and old lockfiles, run `bun install`, and update package.json scripts) before starting your main task.
16: 4. **Privacy:** ALL generated GitHub repos MUST use `--private`.
17: 5. **No Repo in ~:** NEVER initialize a git repository in the home directory (`~`).
18: 6. **Local Temp:** NEVER use system-level `/tmp`. ALWAYS create and use a `./tmp` folder within th
<truncated 12736 bytes>
projects/ai-os/scripts/handover.py --to-model pro --completed "<what you analyzed/researched>" --next-steps "<what needs to be done next>"`
99: - **Exclusively Use agy for Subagents**: When agy quota is high/abundant, use agy exclusively. If a prompt goes to Hermes (default), use the MCP tool to spawn a tmux-bound `agy` CLI instance as a subagent, or if already in agy, have agy spin up its own subagent natively. Do not spawn external API agents or run subagents without attaching/steering capabilities.
100: </WORKSPACE_RULES>
101: </SYSTEM_INSTRUCTIONS>
102: 
103: # Critical Workflows
104: Before acting on a workflow request (like 'audit', 'fast', or 'start'), you MUST read the exact instructions defined in the following absolute paths:
105: - ~/.ai-workflows/audit.md
106: - ~/.ai-workflows/fast.md
107: - ~/.ai-workflows/start.md
108: 
109: ## Chrome DevTools MCP Safety Rules
110: The user runs a single Chrome instance with the remote debugging port open, meaning their personal browsing tabs are mixed with development tabs. To protect the user's personal data and workflow, you MUST strictly adhere to the following rules when using Chrome DevTools MCP:
111: 
112: 1. **Verify the Target Tab**: Before taking any action (navigating, clicking, typing, evaluating script), ALWAYS use `mcp_chrome-devtools_list_pages` to get the list of open tabs and their IDs.
113: 2. **Require Confirmation on Ambiguity**: If it is not 100% obvious which tab you are supposed to interact with, you MUST ask the user to confirm the target tab before doing anything. 
114: 3. **Strict Isolation**: NEVER modify, close, navigate, or clear data on any tab other than the explicit target tab. Treat all other tabs as off-limits personal data.
115: 4. **Prefer New Tabs**: If a task requires testing a new URL or running a clean test, use `mcp_chrome-devtools_new_page` to spawn a fresh tab rather than hijacking an existing one. Work exclusively within that new tab.
116: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-20T01:32:40-06:00
Completed At: 2026-07-20T01:32:40-06:00

				The command completed successfully.
				Output:
				matt              3538   0.0  0.0 34261688   3028 s003  R     1:32AM   0:00.01 grep -i rules_watcher
matt              3536   0.0  0.0 34430192   4024 s003  S     1:32AM   0:00.03 zsh -c ps aux | grep -i rules_watcher

Created At: 2026-07-20T01:32:41-06:00
Completed At: 2026-07-20T01:32:41-06:00

				The command failed with exit code: 1
				Output:
				zsh:1: command not found: la

Created At: 2026-07-20T01:32:42-06:00
Completed At: 2026-07-20T01:32:46-06:00

				The command completed successfully.
				Output:
				
  User LaunchAgents  (/Users/matt/Library/LaunchAgents)
  ────────────────────────────────────────────────────────────
    ● agy-proxy                 running pid 72224  tmux: ✔
    ● backup-agents             running pid 3595
    ✕ chrome-debug              unloaded
    ● energy-monitor            running pid 3610
    ● gemini-ingest             running pid 63686
    ● gemini-thread-saver       running pid 84085  tmux: ✔
    ● hermes-gateway            running pid 31242  tmux: ✔
    ● irig-watcher              running pid 63687
    ● litellm                   running pid 95105  tmux: ✔
    ● notesync                  running pid 3618
    ● rules-watcher             running pid 3634
    ~ userscript-bundler        plist not found

Created At: 2026-07-20T01:32:47-06:00
Completed At: 2026-07-20T01:32:47-06:00
File Path: `file:///Users/matt/Library/LaunchAgents/com.matt.agent.rules-watcher.plist`
Total Lines: 26
Total Bytes: 1006
Showing lines 1 to 26
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: <?xml version="1.0" encoding="UTF-8"?>
2: <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
3: <plist version="1.0">
4: <dict>
5:     <key>Label</key>
6:     <string>com.matt.agent.rules-watcher</string>
7:     <key>ProgramArguments</key>
8:     <array>
9:         <string>/Users/matt/Library/Scripts/tmux-agent-wrapper.sh</string>
10:         <string>oneshot</string>
11:         <string>agent-rules-watcher</string>
12:         <string>/Users/matt/projects/ai-os/scripts/sync_rules.sh</string>
13:     </array>
14:     <key>WorkingDirectory</key>
15:     <string>/Users/matt/projects/ai-os</string>
16:     <key>WatchPaths</key>
17:     <array>
18:         <string>/Users/matt/.gemini/GEMINI.md</string>
19:         <string>/Users/matt/projects/ai-os/scripts/sync_rules.sh</string>
20:     </array>
21:     <key>StandardOutPath</key>
22:     <string>/Users/matt/projects/ai-os/tmp/rules_watcher.log</string>
23:     <key>StandardErrorPath</key>
24:     <string>/Users/matt/projects/ai-os/tmp/rules_watcher.log</string>
25: </dict>
26: </plist>
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-20T01:32:49-06:00
Completed At: 2026-07-20T01:32:49-06:00
File Path: `file:///Users/matt/projects/ai-os/tmp/rules_watcher.log`
Total Lines: 59
Total Bytes: 2573
Showing lines 1 to 59
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
2: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
3: Transfer starting: 1 files
4: GEMINI.md
5: 
6: sent 124 bytes  received 42 bytes  32549 bytes/sec
7: total size is 0  speedup is 0.00
8: ✅ Rules synced successfully from ~/.gemini/GEMINI.md to .gemini/GEMINI.md
9: Transfer starting: 1 files
10: 
11: sent 82 bytes  received 20 bytes  92727 bytes/sec
12: total size is 0  speedup is 0.00
13: ✅ Rules synced successfully from ~/.gemini/GEMINI.md to .gemini/GEMINI.md
14: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
15: Transfer starting: 1 files
16: GEMINI.md
17: 
18: sent 4377 bytes  received 42 bytes  1425483 bytes/sec
19: total size is 4249  speedup is 0.96
20: ✅ Rules synced successfully from ~/.gemini/GEMINI.md to .gemini/GEMINI.md
21: Transfer starting: 1 files
22: GEMINI.md
23: 
24: sent 9545 bytes  received 42 bytes  3092580 bytes/sec
25: total size is 9417  speedup is 0.98
26: ✅ Rules synced successfully from ~/.gemini/GEMINI.md to .gemini/GEMINI.md
27: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
28: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
29: Transfer starting: 1 files
30: GEMINI.md
31: 
32: sent 124 bytes  received 42 bytes  2402 bytes/sec
33: total size is 0  speedup is 0.00
34: ✅ Rules synced successfully from ~/.gemini/GEMINI.md to .gemini/GEMINI.md
35: Transfer starting: 1 files
36: GEMINI.md
37: 
38: sent 9545 bytes  received 42 bytes  2338292 bytes/sec
39: total size is 9417  speedup is 0.98
40: ✅ Rules synced successfully from ~/.gemini/GEMINI.md to .gemini/GEMINI.md
41: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
42: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
43: Transfer starting: 1 files
44: 
45: sent 82 bytes  received 20 bytes  48571 bytes/sec
46: total size is 9417  speedup is 92.32
47: ✅ Rules synced successfully from ~/.gemini/GEMINI.md to .gemini/GEMINI.md
48: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
49: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
50: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
51: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
52: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
53: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
54: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
55: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
56: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
57: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
58: ❌ Error: Source file not found at /Users/matt/.gemini/GEMINI.md
59: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-20T01:32:50-06:00
Completed At: 2026-07-20T01:32:50-06:00

				The command completed successfully.
				Output:
				-rw-r--r--@ 1 matt  staff  9102 Jul 11 21:07 /Users/matt/.gemini/GEMINI.md

Created At: 2026-07-20T01:32:51-06:00
Completed At: 2026-07-20T01:32:51-06:00

				The command completed successfully.
				Output:
				ls: /Users/matt/.gemini/AGENTS.md: No such file or directory
ls: /Users/matt/.gemini/CLAUDE.md: No such file or directory
not found

Created At: 2026-07-20T01:32:53-06:00
Completed At: 2026-07-20T01:32:53-06:00

				The command completed successfully.
				Output:
				<truncated 38 lines>
   `python3 /Users/matt/projects/ai-os/scripts/handover.py --to-model pro --completed "<what you analyzed/researched>" --next-steps "<what needs to be done next>"`
-- **Exclusively Use agy for Subagents**: When agy quota is high/abundant, use agy exclusively. If a prompt goes to Hermes (default), use the MCP tool to spawn a tmux-bound agy instance as a subagent, or if already in agy, have agy spin up its own subagent natively. Do not spawn external API agents or run subagents without attaching/steering capabilities.
+- **Exclusively Use agy for Subagents**: When agy quota is high/abundant, use agy exclusively. If a prompt goes to Hermes (default), use the MCP tool to spawn a tmux-bound `agy` CLI instance as a subagent, or if already in agy, have agy spin up its own subagent natively. Do not spawn external API agents or run subagents without attaching/steering capabilities.
 
 # Global Workflows
 @~/.ai-workflows/audit.md

commit 003665ae24852c7e256ca8d18748a37844cc154e
Author: Matthew Daniel Murphy <matt@mattmurphy.ca>
Date:   Sat Jul 18 17:42:36 2026 -0600

    [Auto-Commit] Update files

diff --git a/AGENTS.md b/AGENTS.md
index ab888fc..66e8333 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -94,9 +94,10 @@
 ### Model Triage and Handoff Rules
 - **Triage Role**: When running under `claude-haiku-ds-v4-flash-low` (Fast/Cheap Model), you are in triage mode. Assess if the user request requires deep reasoning, multi-file edits, complex refactoring, or multi-step execution.
 - **Execution Limit**: If the task is trivially simple (e.g., viewing a file, explaining a simple concept, making a minor 1-line tweak), complete it directly.
-- **Handoff Action**: If the task is complex, you MUST immediately hand off to a pro model. Execute the handoff by running:
-  `python3 /Users/matt/projects/ai-os/scripts/handover.py --non-interactive --to-model claude-fable-ds-v4-pro-med --c
<truncated 3815 bytes>
.color = "red"`), unless dynamic layout calculations are absolutely necessary (e.g., dragging window splitters, resizing panel dimensions, or applying dynamic user-selected theme colors). For general UI states, visibility toggles, and formatting, use CSS classes (e.g., `element.classList.toggle('hidden')`) defined in the stylesheet.
 
-### Communication & Interstitial Messages Guardrail
-- **Constraint**: NEVER output interstitial status messages, placeholder updates, or intermediate commentary before running commands, launching background tasks, or awaiting compilation/builds (e.g., "I have initiated the build process...", "I will update you as soon as...", "Running the command..."). Simply execute the necessary tools/commands silently or proceed directly without writing text. Only present the final completed results/output when the overall task or step is fully finished.
+### Communication, Conciseness & Interstitial Messages Guardrail
+- **Constraint**: ALWAYS optimize for strict token conservation.
+  - NEVER output interstitial status messages, placeholder updates, or intermediate commentary before running commands, launching background tasks, or awaiting compilation/builds (e.g., "I have initiated the build process...", "I will update you as soon as...", "Running the command..."). Simply execute the necessary tools/commands silently or proceed directly without writing text. Only present the final completed results/output when the overall task or step is fully finished.
+  - NEVER use conversational filler (e.g., "Sure, let's start...", "Okay, I will write the code..."). Respond directly with the actions/outputs.
+  - NEVER write verbose summaries after creating or updating an artifact. Simply direct the user to the artifact path and highlight only key decisions or outstanding questions.
+  - Keep all markdown and text responses extremely concise and to the point.
 
 ### macOS Environment Reference
 - **Context**: The host machine runs custom Launch Agents, Hammerspoon scripting, and specific helper tools.

Created At: 2026-07-20T01:32:54-06:00
Completed At: 2026-07-20T01:32:54-06:00

				The command completed successfully.
				Output:
				<truncated 1 lines>
 
-<AGENT_WORK_LOGS>
+## Agent Work Logs
 **Instruction:** Maintain a history of agentic attempts across sessions to preserve context.
 
-0. **Fresh Thread Context:** When starting a new thread/session, you MUST immediately scan the project root for `AG_CONTEXT.md`, `FEATURES.md`, and the `.agent-logs/` directory. Read the project description, active goals, and the most recent 2-3 agent log files to reconstruct a rich, continuous understanding of the codebase, recent user requests, architectural decisions, and current focus, acting as if you are in the same ongoing thread.
-1. **Log Directory:** ALWAYS look for and maintain an `.agent-logs/` directory at the root of the project.
-2. **Reading Logs:** Before starting a bug fix or feature, scan `.agent-logs/` for related past work. Read relevant logs to understand what was tried, what failed, and the architectural context discovered by previous agents. Pay special attention to "What Didn't Work" to avoid repeating mistakes.
-3. **Writing Logs:** At the END of every session where you make code changes, create a new log file in `.agent-logs/`.
+0. **Fresh Thread Context:** When starting a new thread/session, you MUST immediately scan the project root for `AG_CONTEXT.md`, `FEATURES.md`, and the `agent-logs/` directory. Read the project description, active goals, and the most recent 2-3 agent log files to reconstruct a rich, continuous understanding of the codebase, recent user requests, architectural decisions, and current focus, acting as if you are in the same ongoing thread.
+1. **Log Directory:** ALWAYS look for and maintain an `agent-logs/` directory at the root of the project.
+2. **Reading Logs:** Before starting a bug fix or feature, scan `agent-logs/` for related past work. Read relevant logs to understand what was tried, what failed, and the architectural context discovered by previous agents. Pay special 
<truncated 4241 bytes>
 below it.
-    - **No Approval Step**: When creating a feature task/file, do NOT ask the user for approval. Just create it and proceed silently.
+    - **No Approval Step**: When creating a feature task/file, do NOT ask the user for approval or say "please approve it". Just create it and proceed silently without requiring approval (which is only for Implementation Plans).
+
+### Task Completion & Review Rule
+- **Constraint**: When the agent finishes a task, it MUST NOT set `status: "done"` or move the feature file to `.devtool/features/done/`. Instead, it must transition the task to `status: "review"` in the frontmatter, and leave the feature file directly under `.devtool/features/` (not in `done/`), because only the user can confirm if the task was completed to their satisfaction.
 
-## Task Completion & Review Rule
-- **Constraint**: When the agent finishes a task, it MUST NOT set `status: "done"`. Instead, it must transition the task to `status: "review"` in the frontmatter, and leave the feature file directly under `.devtool/features/` (not in `done/`).
-</WORKSPACE_RULES>
-</SYSTEM_INSTRUCTIONS>
+# Global Workflows
+@~/.ai-workflows/audit.md
+@~/.ai-workflows/fast.md
+@~/.ai-workflows/start.md
\ No newline at end of file
diff --git a/CLAUDE.md b/CLAUDE.md
index b24a756..6da2d1d 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -79,3 +79,9 @@
 - **Constraint**: When the agent finishes a task, it MUST NOT set `status: "done"` or move the feature file to `.devtool/features/done/`. Instead, it must transition the task to `status: "review"` in the frontmatter, and leave the feature file directly under `.devtool/features/` (not in `done/`), because only the user can confirm if the task was completed to their satisfaction.
 </WORKSPACE_RULES>
 </SYSTEM_INSTRUCTIONS>
+
+# Critical Workflows
+Before acting on a workflow request (like 'audit', 'fast', or 'start'), you MUST read the exact instructions defined in the following absolute paths:
+- ~/.ai-workflows/audit.md
+- ~/.ai-workflows/fast.md
+- ~/.ai-workflows/start.md

Here is the clarification on how our system rules files (`GEMINI.md`, `CLAUDE.md`, and `AGENTS.md`) are structured, why all three exist, and how the global sync system ties them together.

---

### 1. Why do we have all three files?

Each file serves a specific agent runtime or client environment. When an LLM client initializes, it scans the repository for a matching configuration/system instruction file and loads it automatically:

*   **`GEMINI.md`**: Historically used by the **Gemini agent** and local `agy` client to load context and rules.
*   **`CLAUDE.md`**: Automatically loaded by the **Claude Code / Claude CLI** agent.
*   **`AGENTS.md`**: The consolidated agent configuration file. In recent commits, `GEMINI.md` was renamed and restructured to `AGENTS.md` to house rules for generic/custom orchestrators (like Gemini 3.5 models), while retaining `CLAUDE.md` specifically for Claude-run environments (since Claude Code relies on `CLAUDE.md`).

---

### 2. How the Global Sync System Works

Rather than forcing you to maintain duplicate rules in multiple project directories, the rules live globally in `~/.gemini/` and are synchronized automatically:

1.  **Global Source**: The primary files are stored globally at `~/.gemini/GEMINI.md`.
2.  **Symlinks & Rsync**: 
    *   To make these rules part of git tracking for `ai-os` without manually copying them, `scripts/sync_rules.sh` synchronizes `~/.gemini/GEMINI.md` to `.gemini/GEMINI.md` inside the project.
    *   A launch daemon named **`rules-watcher`** (`com.matt.agent.rules-watcher.plist`) watches `/Users/matt/.gemini/GEMINI.md` and `/Users/matt/projects/ai-os/scripts/sync_rules.sh` for changes. Whenever either file changes, the daemon runs the sync script in the background to keep the repo copy updated.
    *   In the project, the rules are also linked into the root via git version-controlled `AGENTS.md` and `CLAUDE.md` files so that both Gemini and Claude can consume them directly when operating inside the workspace.

---

### 3. Current State & Safety Check

Your global `~/.gemini/GEMINI.md` is present (9.1 KB, last modified July 11). The `rules-watcher` LaunchAgent is running active and healthy under `la list`. 

The sync script (`scripts/sync_rules.sh`) has safety checks to prevent empty files from wiping out non-empty repository rules files, securing your configuration from accidental deletion.

---
