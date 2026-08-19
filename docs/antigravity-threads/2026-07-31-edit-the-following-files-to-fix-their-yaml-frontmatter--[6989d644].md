---
title: "Edit the following files to fix their YAML frontmatter:"
date: "2026-07-31"
conversation_id: "6989d644-a17d-4eb7-b4a1-55a3e2f78606"
source: "antigravity"
---

# Edit the following files to fix their YAML frontmatter:

## User

Please edit the following files to fix their YAML frontmatter:

1. In `/Users/matt/.gemini/config/global_workflows/planner.md` and `/Users/matt/.ai-workflows/planner.md`:
Change:
```yaml
description: MANDATORY: Initiate high-reasoning planning via agymcp (Gemini 3.1 Pro Low) before executing non-trivial tasks.
name: planner
```
To:
```yaml
name: planner
description: "MANDATORY: Initiate high-reasoning planning via agymcp (Gemini 3.1 Pro Low) before executing non-trivial tasks."
```
(Quoting the description value to avoid the invalid YAML colon parsing error).

2. In `/Users/matt/.gemini/config/global_workflows/fast.md` and `/Users/matt/.ai-workflows/fast.md` (if it exists):
Change the empty description to:
```yaml
description: "Analyze and run tasks under a strict efficiency constraint."
```
Verify the files exist and modify them using replace_file_content.

---

## Assistant

Created At: 2026-07-31T15:38:37-06:00
Completed At: 2026-07-31T15:38:37-06:00

				The command exited with code 0.
				Output:
				-rw-r--r--@ 1 matt  staff  394 Jul 26 13:33 /Users/matt/.ai-workflows/fast.md
-rw-r--r--@ 1 matt  staff  595 Jul 31 15:34 /Users/matt/.ai-workflows/planner.md
lrwxr-xr-x@ 1 matt  staff   33 Jul 10 11:27 /Users/matt/.gemini/config/global_workflows/fast.md -> /Users/matt/.ai-workflows/fast.md
-rw-r--r--@ 1 matt  staff  595 Jul 31 15:33 /Users/matt/.gemini/config/global_workflows/planner.md

Created At: 2026-07-31T15:38:38-06:00
Completed At: 2026-07-31T15:38:38-06:00
File Path: `file:///Users/matt/.gemini/config/global_workflows/planner.md`
Total Lines: 12
Total Bytes: 595
Showing lines 1 to 12
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: ---
2: description: MANDATORY: Initiate high-reasoning planning via agymcp (Gemini 3.1 Pro Low) before executing non-trivial tasks.
3: name: planner
4: ---
5: 
6: Run high-reasoning planning using the `planner` skill instructions in `/Users/matt/.gemini/config/skills/planner/SKILL.md`.
7: 
8: 1. Do NOT inspect codebase files directly in the main thread.
9: 2. Delegate context pre-fetching to a Flash subagent.
10: 3. Call `agymcp:agy` (or `agymcp:agy_start`) with the specified model profile to author `implementation_plan.md`.
11: 4. Store the returned `SESSION_ID` for Stage 4 QA audit resumption (`agymcp:agy_continue`).
12: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T15:38:39-06:00
Completed At: 2026-07-31T15:38:39-06:00
File Path: `file:///Users/matt/.ai-workflows/fast.md`
Total Lines: 9
Total Bytes: 394
Showing lines 1 to 9
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: ---
2: name: fast
3: description:
4: ---
5: 1. Analyze the user's next prompt under a strict efficiency constraint.
6: 2. Completely bypass multi-step internal planning, task lists, and file structure mapping.
7: 3. Move straight to outputting the code diff or direct text response.
8: 4. If the request is a trivial change, return *only* the modified code block—absolutely no conversational filler or summaries.
9: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T15:38:40-06:00
Completed At: 2026-07-31T15:38:40-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/.gemini/config/global_workflows/planner.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -1,6 +1,6 @@
 ---
-description: MANDATORY: Initiate high-reasoning planning via agymcp (Gemini 3.1 Pro Low) before executing non-trivial tasks.
 name: planner
+description: "MANDATORY: Initiate high-reasoning planning via agymcp (Gemini 3.1 Pro Low) before executing non-trivial tasks."
 ---
 
 Run high-reasoning planning using the `planner` skill instructions in `/Users/matt/.gemini/config/skills/planner/SKILL.md`.
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-07-31T15:38:41-06:00
Completed At: 2026-07-31T15:38:41-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/.ai-workflows/planner.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -1,6 +1,6 @@
 ---
-description: MANDATORY: Initiate high-reasoning planning via agymcp (Gemini 3.1 Pro Low) before executing non-trivial tasks.
 name: planner
+description: "MANDATORY: Initiate high-reasoning planning via agymcp (Gemini 3.1 Pro Low) before executing non-trivial tasks."
 ---
 
 Run high-reasoning planning using the `planner` skill instructions in `/Users/matt/.gemini/config/skills/planner/SKILL.md`.
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-07-31T15:38:42-06:00
Completed At: 2026-07-31T15:38:42-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/.ai-workflows/fast.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -1,6 +1,6 @@
 ---
 name: fast
-description:
+description: "Analyze and run tasks under a strict efficiency constraint."
 ---
 1. Analyze the user's next prompt under a strict efficiency constraint.
 2. Completely bypass multi-step internal planning, task lists, and file structure mapping.
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-07-31T15:38:43-06:00
Completed At: 2026-07-31T15:38:43-06:00
Message sent to "2a5ff4d4-d870-4f7b-bfa6-ad9e951db1d9".

The YAML frontmatter for the requested files has been updated as follows:

*   **[`planner.md`](file:///Users/matt/.gemini/config/global_workflows/planner.md)** and **[`planner.md`](file:///Users/matt/.ai-workflows/planner.md)**: The description has been updated to be quoted to ensure valid YAML parsing.
*   **[`fast.md`](file:///Users/matt/.ai-workflows/fast.md)** (which also updates **[`fast.md`](file:///Users/matt/.gemini/config/global_workflows/fast.md)**): The description has been added as requested.

---
