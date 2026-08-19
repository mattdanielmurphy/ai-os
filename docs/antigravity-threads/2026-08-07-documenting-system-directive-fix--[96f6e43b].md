---
title: "Documenting System Directive Fix"
date: "2026-08-07"
conversation_id: "96f6e43b-94a2-4139-a83a-a6195ff3798e"
source: "antigravity"
---

# Documenting System Directive Fix

## User

1. Create a log file at `/Users/matt/projects/userscript-bundler/agent-logs/2026-08-06_19-56_fix_system_directives_stripping.md` with:
```markdown
# Fix Multi-Line System Directive Stripping in Gemini Web UI

## Problem
In Gemini Web UI, injected system directives (`[SYSTEM CONTEXT & DIRECTIVES: ... ]`) were remaining visible in the rendered user prompt box.

## Root Cause
Gemini Web UI splits multi-line user queries into individual `<p class="query-text-line">` elements inside `<user-query>`. The previous regex matching was running on single `<p>` nodes independently. Since the opening `[SYSTEM CONTEXT & DIRECTIVES:` and closing `]` were on different `<p>` lines, single-line regex matching failed for every line in the block.

## Solution
1. Updated `03-timestamps.js` to iterate over query containers (`user-query`) and track `insideSysDirective` state across paragraph elements (`pNodes`).
2. Cleared clean content and set `display: none` for paragraph elements containing system directive lines so they are visually hidden without leaving empty DOM gaps.
3. Updated `toggleRawPayloadMode` to support toggling display between raw payload mode and clean mode.
4. Rebuilt userscript bundle (`userscript_bundle.js` and `compiled/gemini-enhancements.user.js`).
```

2. Append to `/Users/matt/projects/userscript-bundler/DEVELOPMENT_JOURNAL.md`:
```markdown

## 2026-08-06
- **Fix Multi-Line System Directive Stripping:** Updated `03-timestamps.js` to track multi-line `[SYSTEM CONTEXT & DIRECTIVES:]` state across paragraph nodes in `user-query` containers and hide system directive lines from prompt display. See [agent-logs/2026-08-06_19-56_fix_system_directives_stripping.md](file:///Users/matt/projects/userscript-bundler/agent-logs/2026-08-06_19-56_fix_system_directives_stripping.md).
```

---

## Assistant

Created At: 2026-08-06T19:56:44-06:00
Completed At: 2026-08-06T19:56:44-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-06T19:56:46-06:00
Completed At: 2026-08-06T19:56:46-06:00
Created file file:///Users/matt/projects/userscript-bundler/agent-logs/2026-08-06_19-56_fix_system_directives_stripping.md with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-06T19:56:46-06:00
Completed At: 2026-08-06T19:56:46-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/DEVELOPMENT_JOURNAL.md`
Total Lines: 17
Total Bytes: 2252
Showing lines 1 to 17
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Development Journal
2: 
3: ## 2026-07-21
4: - **Refactor Gemini Thread Saver into Grouped Source Files:** Extended `bundler.js` and `watch-and-bundle.js` with script group capabilities and split `gemini.js` into 10 ordered source files sharing a single IIFE lexical scope under `userscripts/gemini-thread-saver/`. See [.agent-logs/2026-07-21_18-25_gemini-grouped-source-refactor.md](file:///Users/matt/projects/userscript-bundler/.agent-logs/2026-07-21_18-25_gemini-grouped-source-refactor.md).
5: 
6: ## 2026-07-22
7: - **Multi-Module Standalone Compilation:** Updated `bundler.cjs` to compile multi-module (grouped) userscripts like Gemini Thread Saver into standalone `.user.js` files in `./compiled/`. Link to agent log: [.agent-logs/2026-07-22_02-45_multi-module-standalone-compilation.md](file:///Users/matt/projects/userscript-bundler/.agent-logs/2026-07-22_02-45_multi-module-standalone-compilation.md).
8: 
9: ## 2026-07-24
10: - **Gemini Quick Actions & Tool Call Execution:** Added Quick Actions dropdown menu and `save_note` tool call executor to Gemini Enhancements. Link to agent log: [.agent-logs/2026-07-24_01-40_gemini-quick-actions.md](file:///Users/matt/projects/userscript-bundler/.agent-logs/2026-07-24_01-40_gemini-quick-actions.md).
11: 
12: 
13: - **Fix tool call execution logic:** Updated window.scanToolCalls to always display run button and enforce auto-execution condition. [See agent log](file:///Users/matt/.gemini/antigravity/brain/8130b9a3-f269-4c96-8be9-89a2e0c4d68c/agent-logs/2026-07-28_14-53_tool-calls-fix.md)
14: - **Tool Call Directive Update:** Updated `gemini-enhancements/05-prompt-tools.js` to refine the tool call schema and specify `run_automatically` behavior.
15: - **Refine tool execution logic:** Updated  to enable run button unconditionally and adjust auto-execute condition. [2026-07-28_15-00-refine-tool-execution.md](file:///Users/matt/.gemini/antigravity/brain/7ac774e3-9dea-4924-b8df-c7a48b731a2d/2026-07-28_15-00-refine-tool-execution.md)
16: - **Refine tool execution logic:** Updated 10-tool-calls.js to enable run button unconditionally and adjust auto-execute condition. [2026-07-28_15-00-refine-tool-execution.md](file:///Users/matt/.gemini/antigravity/brain/7ac774e3-9dea-4924-b8df-c7a48b731a2d/2026-07-28_15-00-refine-tool-execution.md)
17: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-06T19:56:49-06:00
Completed At: 2026-08-06T19:56:49-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/userscript-bundler/DEVELOPMENT_JOURNAL.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -14,4 +14,8 @@
 - **Tool Call Directive Update:** Updated `gemini-enhancements/05-prompt-tools.js` to refine the tool call schema and specify `run_automatically` behavior.
 - **Refine tool execution logic:** Updated  to enable run button unconditionally and adjust auto-execute condition. [2026-07-28_15-00-refine-tool-execution.md](file:///Users/matt/.gemini/antigravity/brain/7ac774e3-9dea-4924-b8df-c7a48b731a2d/2026-07-28_15-00-refine-tool-execution.md)
 - **Refine tool execution logic:** Updated 10-tool-calls.js to enable run button unconditionally and adjust auto-execute condition. [2026-07-28_15-00-refine-tool-execution.md](file:///Users/matt/.gemini/antigravity/brain/7ac774e3-9dea-4924-b8df-c7a48b731a2d/2026-07-28_15-00-refine-tool-execution.md)
+
+
+## 2026-08-06
+- **Fix Multi-Line System Directive Stripping:** Updated `03-timestamps.js` to track multi-line `[SYSTEM CONTEXT & DIRECTIVES:]` state across paragraph nodes in `user-query` containers and hide system directive lines from prompt display. See [agent-logs/2026-08-06_19-56_fix_system_directives_stripping.md](file:///Users/matt/projects/userscript-bundler/agent-logs/2026-08-06_19-56_fix_system_directives_stripping.md).
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-06T19:56:50-06:00
Completed At: 2026-08-06T19:56:50-06:00
Message sent to "ee1b915f-4a03-4015-b194-2fda62be71b5".

The requested actions have been completed:

1.  **Log File Created:** The log file `/Users/matt/projects/userscript-bundler/agent-logs/2026-08-06_19-56_fix_system_directives_stripping.md` was created with the specified content.
2.  **Development Journal Updated:** The entry for `2026-08-06` regarding the "Fix Multi-Line System Directive Stripping" was successfully appended to `/Users/matt/projects/userscript-bundler/DEVELOPMENT_JOURNAL.md`.

---
