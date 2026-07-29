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
   - The main orchestrator MUST immediately spawn a research subagent (`invoke_subagent` with `TypeName: "research"` or `Model: "flash"`) to inspect the project structure and gather necessary file context into a summary report.

2. **Step 2: External Planner Pass via `agymcp`**
   - The orchestrator passes the subagent's research report to the requested model profile (e.g., `gemini-3.1-pro-high` or `pro`) using the `agymcp` tool or specialized planner subagent (`invoke_subagent` with `Model: "pro"`).
   - The external planner generates the `implementation_plan.md` artifact at `<appDataDir>/brain/<conversation-id>/implementation_plan.md`.

3. **Step 3: Plan Execution (Main Orchestrator -> Flash Subagent -> Flash-Lite Edits)**
   - Once user approves plan, Main Orchestrator (M) spawns an execution orchestrator subagent (Model: 'flash').
   - The Flash execution subagent coordinates the sub-tasks and delegates individual file creation/edit operations to leaf 'flash_lite' subagents (E).

## Core Directives
- **Zero Direct Codebase Inspection in Main Thread**: Let research subagents collect context.
- **Zero Direct Plan Drafts by Orchestrator**: High-reasoning plans MUST originate from the designated Pro/Planner model.
