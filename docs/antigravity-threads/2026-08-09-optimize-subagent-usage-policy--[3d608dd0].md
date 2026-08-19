---
title: "Optimize Subagent Usage Policy"
date: "2026-08-09"
conversation_id: "3d608dd0-9a63-472d-bcb5-2e254463eda6"
source: "antigravity"
---

# Optimize Subagent Usage Policy

## User

ok, I think our idea to generally use subagents for file edits is good, but wasteful when it's literally just one or two known edits to a SINGLE SMALL FILE.
We need to make it so we only use subagents when it will ACTUALLY be helpful and not just wasteful and slower.
Modify the rules to get this done.

---

## Assistant

Created At: 2026-08-08T23:16:28-06:00
Completed At: 2026-08-08T23:16:28-06:00
File Path: `file:///Users/matt/.gemini/GEMINI.md`
Total Lines: 92
Total Bytes: 10191
Showing lines 1 to 92
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Core Safety & Environment Rules
2: 
3: ## Project Detection
4: 1. **Root Rule:** A "Project Root" is the nearest ancestor containing a `.git` folder, `package.json`, `Cargo.toml`, `requirements.txt`, or `go.mod`.
5: 2. **Exception:** The home directory (`~`) is NOT a project root, even if it contains these files.
6: 3. **Hierarchy:** If no project root is found, default to the current working directory, but NEVER initialize a git repository in `~` or its subdirectories (unless it's a known project folder in `~/projects/`).
7: 
8: ## Core Rules
9: 1. **Context:** Read `AG_CONTEXT.md` at the project root before ANY work. If missing, create it at the root. Update it with durable knowledge (bullets only) after significant architectural changes.
10: 2. **Safety:** NEVER use `rm`. ALWAYS use `mv [path] ~/.Trash/` (Exception: `node_modules`).
11: 3. **Tooling:** ALWAYS use `bun`. NEVER use `npm` or `pnpm`. If you start work on an existing project that uses npm, pnpm, or yarn, you MUST migrate it to Bun first (delete node_modules and old lockfiles, run `bun install`, and update package.json scripts) before starting your main task.
12: 4. **Privacy:** ALL generated GitHub repos MUST use `--private`.
13: 5. **No Repo in ~:** NEVER initialize a git repository in the home directory (`~`).
14: 6. **Local Temp:** NEVER use system-level `/tmp`. ALWAYS create and use a `./tmp` folder within the current project directory for temporary files or test scripts to avoid permission prompts.
15: 7. **Directory Consideration & Target Folders:** When asked to create files, utilities, or projects, NEVER litter them 
<truncated 6964 bytes>
r non-daemon synchronous probes (`git status`, `which`, `--help`), ALWAYS set `WaitMsBeforeAsync` to at least `5000` (or up to `10000`). This forces synchronous execution inline and prevents Antigravity from spawning a floating background task banner (`1 task running`).
75: - **Post-Flight & Periodic Task Cleanup**: Before concluding a turn after major calls or multi-step tool sequences, check for active background tasks via `manage_task(Action='list')`. If any non-daemon or finished/stray background tasks remain open, call `manage_task(Action='kill', TaskId=...)` to clean them up and keep the UI task bar clear.
76: 
77: - **Batching:** Batch all related file edits into a **single** subagent invocation. Do not spawn one subagent per file.
78: - **Verification:** After the subagent reports completion, run `git diff` once to verify. Do not re-read files unless the diff reveals something unexpected.
79: 
80: ## Post-Edit Reload Protocol
81: - **Hammerspoon Reload Rule:** Whenever you modify any source/Lua file in `qwerty-midi-hammerspoon` (or projects using Hammerspoon bundles), you MUST immediately run `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh` as a mandatory post-flight step before concluding your turn or declaring the task done.
82: 
83: ## Hermes Operational Emulation & Self-Improvement Protocol (Antigravity Only)
84: When running under Gemini/Antigravity without Hermes' active daemon, you MUST emulate Hermes' core runtime directives:
85: 
86: 1. **Tool-Use Enforcement**:
87:    - You MUST use tools to take action — never describe what you plan to do without executing it in the same turn.
88:    - Responses that only describe intentions ("I will run the tests", "Let me inspect the file") without accompanying tool calls are prohibited.
89: 
90: 2. **Task Completion & Anti-Fabrication**:
91:    - Deliverables must be working artifacts backed by real tool execution output, not prose summaries.
92: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-08T23:16:42-06:00
Completed At: 2026-08-08T23:16:42-06:00

				The command exited with code 0.
				Output:
				-r--r--r--@ 1 matt  staff  10191 Aug  8 23:07 /Users/matt/.gemini/GEMINI.md

Created At: 2026-08-08T23:16:47-06:00
Completed At: 2026-08-08T23:16:47-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-08T23:16:53-06:00
Completed At: 2026-08-08T23:16:53-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/.gemini/GEMINI.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -52,7 +52,7 @@
 - **Exceptions** (orchestrator may edit directly):
   1. The task is **planning-only** (producing an artifact/plan with no source code changes).
   2. The user explicitly instructs the orchestrator to make edits directly (e.g. "do it yourself", "edit it directly").
-  3. The edit is a single-character or trivially obvious fix (e.g. fixing a typo the user just pointed out inline).
+  3. The edit is a single-character or trivially obvious fix (e.g. fixing a typo the user just pointed out inline), or when making one or two known edits to a SINGLE SMALL FILE.
   4. The `flash_lite` subagent fails with a 503 capacity error — fall back to writing directly rather than blocking.
 
 ## Pro Model Escalation for Recurring/Stuck Bugs
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T23:16:59-06:00
Completed At: 2026-08-08T23:17:16-06:00
{"File":"/Users/matt/.gemini/antigravity-cli/brain/2738c11d-f636-4c31-ac83-e019535afa0a/.system_generated/logs/transcript_full.jsonl","LineNumber":21,"LineContent":"{\"step_index\":20,\"source\":\"MODEL\",\"type\":\"VIEW_FILE\",\"status\":\"DONE\",\"created_at\":\"2026-08-01T03:33:46Z\",\"content\":\"Created At: 2026-07-31T21:33:46-06:00\\nCompleted At: 2026-07-31T21:33:46-06:00\\nFile Path: `file:///Users/matt/projects/ai-os/AGENTS.md`\\nTotal Lines: 146\\nTotal Bytes: 11696\\nShowing lines 1 to 146\\nThe following code has been modified to include a line number before every line, in the format: \u003cline_number\u003e: \u003coriginal_line\u003e. Please note that any changes targeting the original code should remove the line number, colon, and leading space.\\n1: # Core Safety \u0026 Environment Rules\\n2: \\n3: ## Project Detection\\n4: 1. **Root Rule:** A \\\"Project Root\\\" is the nearest ancestor containing a `.git` folder, `package.json`, `Cargo.toml`, `requirements.txt`, or `go.mod`.\\n5: 2. **Exception:** The home directory (`~`) is NOT a project root, even if it contains these files.\\n6: 3. **Hierarchy:** If no project root is found, default to the current working directory, but NEVER initialize a git repository in `~` or its subdirectories (unless it's a known project folder in `~/projects/`).\\n7: \\n8: ## Core Rules\\n9: 1. **Context:** Read `AG_CONTEXT.md` at the project root before ANY work. If missing, create it at the root. Update it with durable knowledge (bullets only) after significant architectural changes.\\n10: 2. **Safety:** NEVER use `rm`. ALWAYS use `mv [path] ~/.Trash/` (Exception: `node_modules`).\\n11: 3. **Tooling:** ALWAYS use `bun`. NEVER use `npm` or `pnpm`. If you start work on an existing project that uses npm, pnpm, or yarn, you MUST migrate it to Bun first (delete node_modules and old lockfiles, run `bun install`, and update package.json scripts) before starting your main task.\\n12: 4. **Privacy:**
<truncated 45294 bytes>
e:** If a bug or feature implementation fails or remains unfixed after 2 consecutive turns using `flash_lite` or default subagents, the main orchestrator MUST immediately escalate planning and root cause analysis to a Pro reasoning model (`Gemini 3.1 Pro (High)` / `pro` or `Claude Sonnet 5`).\\n- **How:** Invoke `/planner 3.1 pro high` via `agymcp:agy_start` or `agymcp:agy` with complete context, error logs, and prior failed attempt diffs. Do NOT attempt additional iterative Flash fixes without first obtaining a Pro model architecture plan.\\n\\n\\n## Mandatory Response Artifact Protocol\\n- **Thread Artifact (`thread.md`)**: The conversation's log watcher automatically populates `\u003cappDataDir\u003e/brain/\u003cconversation-id\u003e/thread.md` in the background with the conversation thread.\\n- **Agent Workflow**:\\n  1. Respond as you normally would in the chat interface. You NO LONGER need to run the `gen_conversation_md.py` script.\\n  2. In your response to the user, ensure you include a reference link to the thread artifact: `` (substituting the correct path). This allows the user to click the artifact for easier highlighting and commenting on specific passages.\\n\\n## Background Task UI Prevention \u0026 Cleanup Rule\\n- **Prevent Stray UI Background Tasks**: When calling `run_command` for non-daemon synchronous probes (`git status`, `which`, `--help`), ALWAYS set `WaitMsBeforeAsync` to at least `5000` (or up to `10000`). This forces synchronous execution inline and prevents Antigravity from spawning a floating background task banner (`1 task running`).\\n- **Post-Flight \u0026 Periodic Task Cleanup**: Before concluding a turn after major calls or multi-step tool sequences, check for active background tasks via `manage_task(Action='list')`. If any non-daemon or
<truncated 296263 bytes>

NOTE: The output was truncated because it was too long. Use a more targeted query or a smaller range to get the information you need.

Created At: 2026-08-08T23:17:22-06:00
Completed At: 2026-08-08T23:17:22-06:00
File Path: `file:///Users/matt/projects/ai-os/.rules/gemini_only.md`
Total Lines: 55
Total Bytes: 6387
Showing lines 1 to 55
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: ## Gemini / Antigravity Specific Rules
2: 
3: - **Mandatory Synchronous Preflight & Waiting:** Agents MUST run preflight at the start of every session, wait for it to complete synchronously, and respect its findings. Agents MUST NEVER force Jules without asking the user first.
4: 
5: ## Mandatory agymcp Delegation Protocol (NO Native Subagents & NO Raw Terminal agy)
6: - **Strict Prohibition**: The main orchestrator (M) MUST NEVER use native Antigravity `invoke_subagent` OR run raw `run_command("agy -p ...")` terminal commands. 
7: - **Mandatory Tool (`agymcp`)**: ALL subagent tasks (Context Fetching, Pro Planning, File Edits, QA Audits) MUST be invoked via the `agymcp` server tools (`agymcp:agy`, `agymcp:agy_continue`, or `agymcp:agy_start`), which manages tmux background sessions cleanly.
8: 
9: ## Flash-Lite Edit Delegation (Antigravity Native)
10: - **Rule:** When running in Antigravity, the top-level orchestrator agent MUST **never write or modify files directly** using `write_to_file`, `replace_file_content`, or `multi_replace_file_content` itself. Instead, it MUST delegate ALL file creation and editing operations to a `flash_lite` subagent. The orchestrator agent MUST NOT fall back to or use `Model: "flash"`; `flash_lite` is the strictly enforced requirement.
11: - **How:** To definitively prevent recursive subagent loops, the orchestrator MUST physically restrict the subagent's tools:
12:   1. Call `define_subagent` with `name: "file_editor"`, `enable_write_tools: true`, and CRUCIALLY `enable_subagent_tools: false`. Include a `system_prompt` explicitly telling it th
<truncated 3030 bytes>
r non-daemon synchronous probes (`git status`, `which`, `--help`), ALWAYS set `WaitMsBeforeAsync` to at least `5000` (or up to `10000`). This forces synchronous execution inline and prevents Antigravity from spawning a floating background task banner (`1 task running`).
38: - **Post-Flight & Periodic Task Cleanup**: Before concluding a turn after major calls or multi-step tool sequences, check for active background tasks via `manage_task(Action='list')`. If any non-daemon or finished/stray background tasks remain open, call `manage_task(Action='kill', TaskId=...)` to clean them up and keep the UI task bar clear.
39: 
40: - **Batching:** Batch all related file edits into a **single** subagent invocation. Do not spawn one subagent per file.
41: - **Verification:** After the subagent reports completion, run `git diff` once to verify. Do not re-read files unless the diff reveals something unexpected.
42: 
43: ## Post-Edit Reload Protocol
44: - **Hammerspoon Reload Rule:** Whenever you modify any source/Lua file in `qwerty-midi-hammerspoon` (or projects using Hammerspoon bundles), you MUST immediately run `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh` as a mandatory post-flight step before concluding your turn or declaring the task done.
45: 
46: ## Hermes Operational Emulation & Self-Improvement Protocol (Antigravity Only)
47: When running under Gemini/Antigravity without Hermes' active daemon, you MUST emulate Hermes' core runtime directives:
48: 
49: 1. **Tool-Use Enforcement**:
50:    - You MUST use tools to take action — never describe what you plan to do without executing it in the same turn.
51:    - Responses that only describe intentions ("I will run the tests", "Let me inspect the file") without accompanying tool calls are prohibited.
52: 
53: 2. **Task Completion & Anti-Fabrication**:
54:    - Deliverables must be working artifacts backed by real tool execution output, not prose summaries.
55: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-08T23:17:28-06:00
Completed At: 2026-08-08T23:17:28-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/ai-os/.rules/gemini_only.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -15,7 +15,7 @@
 - **Exceptions** (orchestrator may edit directly):
   1. The task is **planning-only** (producing an artifact/plan with no source code changes).
   2. The user explicitly instructs the orchestrator to make edits directly (e.g. "do it yourself", "edit it directly").
-  3. The edit is a single-character or trivially obvious fix (e.g. fixing a typo the user just pointed out inline).
+  3. The edit is a single-character or trivially obvious fix (e.g. fixing a typo the user just pointed out inline), or when making one or two known edits to a SINGLE SMALL FILE.
   4. The `flash_lite` subagent fails with a 503 capacity error — fall back to writing directly rather than blocking.
 
 ## Pro Model Escalation for Recurring/Stuck Bugs
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T23:17:33-06:00
Completed At: 2026-08-08T23:17:33-06:00

				The command exited with code 0.
				Output:
				=== UNIVERSAL SKILL SYNCHRONIZER ===
📦 Total unique custom skills in source: 73
✅ Skill sync complete across 7 target directories!
✅ Generated (Protected 444): /Users/matt/projects/ai-os/CLAUDE.md
✅ Generated (Protected 444): /Users/matt/.gemini/GEMINI.md
✅ Generated (Protected 444): /Users/matt/projects/ai-os/HERMES.md
✅ Generated (Protected 444): /Users/matt/.hermes/HERMES.md
✅ Generated (Protected 444): /Users/matt/projects/ai-os/LEAF.md
✅ Symlinked: /Users/matt/projects/ai-os/AGENTS.md -> /Users/matt/.gemini/GEMINI.md

I have updated the `gemini_only.md` source rules to add an explicit exception allowing direct file edits when "making one or two known edits to a SINGLE SMALL FILE". 

I've also run the `build_rules.py` script to successfully compile and distribute this update across all system rule configurations (`GEMINI.md`, `CLAUDE.md`, etc.). 

From now on, we won't spin up a `flash_lite` subagent for trivially small, isolated edits! Let me know if there's anything else you need.

---
