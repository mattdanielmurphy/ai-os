Project Path: planner_context

Source Tree:

```txt
planner_context
├── SKILL.md
└── planner.md

```

`SKILL.md`:

```md
---
name: planner
description: MANDATORY: Use when initiating high-reasoning planning with a specific model profile before executing non-trivial tasks.
version: 1.3.0
author: AGY Systems
license: MIT
metadata:
  hermes:
    tags: [planner, triage, agymcp, reasoning, planning, multi-stage]
    related_skills: [plan, plan-multi-step, agy]
---

# AGY Planner Skill (`/planner`)

## STRICT TRIAGE & DELEGATION MANDATE

**CRITICAL RULE FOR ORCHESTRATOR**: When the user passes `/planner` or any model arguments (e.g. `/planner 3.1 pro high`), the Orchestrator MUST NEVER do codebase research, file reads (`view_file`), code searches (`grep_search`), or plan authoring directly in the main thread. 

Doing reads or planning directly in the main thread upon receiving `/planner` is a **STRICT SYSTEM VIOLATION**.

## Usage & Model Profiles

Call the skill directly with optional model parameters:
- `/planner` (defaults to Gemini Pro 3.1 Low)
- `/planner 3.1 pro high`
- `/planner pro`
- `/planner claude-3-5-sonnet`

## Mandatory Execution Workflow

1. **Step 1: Immediate Subagent Research Delegation (Flash/Subagent)**
   - The main orchestrator thread MUST NOT call `list_dir`, `view_file`, or `grep_search` on codebase files.
   - The main orchestrator MUST immediately spawn a research subagent using `agymcp:agy` (Model: "flash") to inspect the project structure and gather necessary file context into a summary report.

2. **Step 2: External Planner Pass via `agymcp`**
    - The orchestrator passes the research report to the requested model profile using `agymcp:agy` or `agymcp:agy_start`.
    - The external planner generates the `implementation_plan.md` artifact at `<appDataDir>/brain/<conversation-id>/implementation_plan.md`.
    - **Session Persistence**: When resuming planning or adding follow-up passes after plan failure, the main orchestrator MUST resume the existing `agymcp` session using `agymcp:agy_continue` with the active `SESSION_ID` (or `job_id`). Do NOT spawn a new `agymcp:agy_start` or native subagent session.

3. **Step 3: Plan Execution (Main Orchestrator -> Flash Subagent -> Flash-Lite Edits)**
    - Once user approves plan, Main Orchestrator (M) spawns an execution orchestrator subagent (Model: 'flash').
    - The Flash execution subagent coordinates the sub-tasks and delegates individual file creation/edit operations to leaf 'flash_lite' subagents (E).

## Core Directives
- **Zero Direct Codebase Inspection in Main Thread**: Let research subagents collect context.
- **Zero Direct Plan Drafts by Orchestrator**: High-reasoning plans MUST originate from the designated Pro/Planner model.
- **Session Continuity**: Under NO circumstances should native `invoke_subagent` or new `agymcp:agy_start` sessions be created for follow-up iterations when an existing session is active. Use `agymcp:agy_continue` instead.

```

`planner.md`:

```md
---
name: planner
description: "MANDATORY: Initiate high-reasoning planning via agymcp (Gemini 3.1 Pro Low) before executing non-trivial tasks."
---

Run high-reasoning planning using the `planner` skill instructions in `/Users/matt/.gemini/config/skills/planner/SKILL.md`.

1. Do NOT inspect codebase files directly in the main thread.
2. Delegate context pre-fetching to a Flash subagent.
3. Call `agymcp:agy` (or `agymcp:agy_start`) with the specified model profile to author `implementation_plan.md`.
4. Store the returned `SESSION_ID` for Stage 4 QA audit resumption (`agymcp:agy_continue`).

```