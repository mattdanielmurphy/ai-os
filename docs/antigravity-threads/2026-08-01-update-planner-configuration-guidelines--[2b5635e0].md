---
title: "Update Planner Configuration Guidelines"
date: "2026-08-01"
conversation_id: "2b5635e0-eda8-4b5a-b90a-c548ac72fc63"
source: "antigravity"
---

# Update Planner Configuration Guidelines

## User

Update `/Users/matt/.gemini/config/skills/planner/SKILL.md` to explicitly state:
1. When resuming planning or adding follow-up passes after plan failure, the main orchestrator MUST resume the existing `agymcp` session using `agymcp:agy_continue` with the active `SESSION_ID` (or `job_id`) instead of spawning a new `agymcp:agy_start` or native subagent session.
2. Under NO circumstances should native `invoke_subagent` or new `agymcp:agy_start` sessions be created for follow-up iterations when an existing session is active.

Edit `/Users/matt/.gemini/config/skills/planner/SKILL.md` directly.

---

## Assistant

Created At: 2026-07-31T22:25:06-06:00
Completed At: 2026-07-31T22:25:06-06:00
File Path: `file:///Users/matt/.gemini/config/skills/planner/SKILL.md`
Total Lines: 46
Total Bytes: 2323
Showing lines 1 to 46
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: ---
2: name: planner
3: description: MANDATORY: Use when initiating high-reasoning planning with a specific model profile before executing non-trivial tasks.
4: version: 1.3.0
5: author: AGY Systems
6: license: MIT
7: metadata:
8:   hermes:
9:     tags: [planner, triage, agymcp, reasoning, planning, multi-stage]
10:     related_skills: [plan, plan-multi-step, agy]
11: ---
12: 
13: # AGY Planner Skill (`/planner`)
14: 
15: ## STRICT TRIAGE & DELEGATION MANDATE
16: 
17: **CRITICAL RULE FOR ORCHESTRATOR**: When the user passes `/planner` or any model arguments (e.g. `/planner 3.1 pro high`), the Orchestrator MUST NEVER do codebase research, file reads (`view_file`), code searches (`grep_search`), or plan authoring directly in the main thread. 
18: 
19: Doing reads or planning directly in the main thread upon receiving `/planner` is a **STRICT SYSTEM VIOLATION**.
20: 
21: ## Usage & Model Profiles
22: 
23: Call the skill directly with optional model parameters:
24: - `/planner` (defaults to Gemini Pro 3.1 Low)
25: - `/planner 3.1 pro high`
26: - `/planner pro`
27: - `/planner claude-3-5-sonnet`
28: 
29: ## Mandatory Execution Workflow
30: 
31: 1. **Step 1: Immediate Subagent Research Delegation (Flash/Subagent)**
32:    - The main orchestrator thread MUST NOT call `list_dir`, `view_file`, or `grep_search` on codebase files.
33:    - The main orchestrator MUST immediately spawn a research subagent using `agymcp:agy` (Model: "flash") to inspect the project structure and gather necessary file context into a summary report.
34: 
35: 2. **Step 2: External Planner Pass via `agymcp`**
36:    - The orchestrator passes the research report to the requested model profile using `agymcp:agy` or `agymcp:agy_start`.
37:    - The external planner generates the `implementation_plan.md` artifact at `<appDataDir>/brain/<conversation-id>/implementation_plan.md`.
38: 
39: 3. **Step 3: Plan Execution (Main Orchestrator -> Flash Subagent -> Flash-Lite Edits)**
40:    - Once user approves plan, Main Orchestrator (M) spawns an execution orchestrator subagent (Model: 'flash').
41:    - The Flash execution subagent coordinates the sub-tasks and delegates individual file creation/edit operations to leaf 'flash_lite' subagents (E).
42: 
43: ## Core Directives
44: - **Zero Direct Codebase Inspection in Main Thread**: Let research subagents collect context.
45: - **Zero Direct Plan Drafts by Orchestrator**: High-reasoning plans MUST originate from the designated Pro/Planner model.
46: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-31T22:25:09-06:00
Completed At: 2026-07-31T22:25:11-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/.gemini/config/skills/planner/SKILL.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -33,12 +33,13 @@
    - The main orchestrator MUST immediately spawn a research subagent using `agymcp:agy` (Model: "flash") to inspect the project structure and gather necessary file context into a summary report.
 
 2. **Step 2: External Planner Pass via `agymcp`**
-   - The orchestrator passes the research report to the requested model profile using `agymcp:agy` or `agymcp:agy_start`.
-   - The external planner generates the `implementation_plan.md` artifact at `<appDataDir>/brain/<conversation-id>/implementation_plan.md`.
+    - The orchestrator passes the research report to the requested model profile using `agymcp:agy` or `agymcp:agy_start`.
+    - The external planner generates the `implementation_plan.md` artifact at `<appDataDir>/brain/<conversation-id>/implementation_plan.md`.
+    - **Session Persistence**: When resuming planning or adding follow-up passes after plan failure, the main orchestrator MUST resume the existing `agymcp` session using `agymcp:agy_continue` with the active `SESSION_ID` (or `job_id`). Do NOT spawn a new `agymcp:agy_start` or native subagent session.
 
 3. **Step 3: Plan Execution (Main Orchestrator -> Flash Subagent -> Flash-Lite Edits)**
-   - Once user approves plan, Main Orchestrator (M) spawns an execution orchestrator subagent (Model: 'flash').
-   - The Flash execution subagent coordinates the sub-tasks and delegates individual file creation/edit operations to leaf 'flash_lite' subagents (E).
+    - Once user approves plan, Main Orchestrator (M) spawns an execution orchestrator subagent (Model: 'flash').
+    - The Flash execution subagent coordinates the sub-tasks and delegates individual file creation/edit operations to leaf 'flash_lite' subagents (E).
 
 ## Core Directives
 - **Zero Direct Codebase Inspection in Main Thread**: Let research subagents collect context.
@@ -45,1 +45,2 @@
+- **Session Continuity**: Under NO circumstances should native `invoke_subagent` or new `agymcp:agy_start` sessions be created for follow-up iterations when an existing session is active. Use `agymcp:agy_continue` instead.
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

We did our best to apply changes despite some inaccuracies. Double check if the edit applied is what you intended.

Created At: 2026-07-31T22:25:11-06:00
Completed At: 2026-07-31T22:25:11-06:00
Message sent to "8a68576b-bf2e-41c5-bd4e-152ee6473fd0".

The file `/Users/matt/.gemini/config/skills/planner/SKILL.md` has been updated with mandatory instructions for session persistence and continuity using `agymcp:agy_continue`.

---
