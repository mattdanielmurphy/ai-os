---
name: _plan-with-gemini
description: "Initiate high-reasoning implementation planning by spawning a native subagent with Gemini 3.7 High without requiring GitHub repo sync."
---

# Plan With Gemini (High Reasoning Subagent)

Initiate deep, high-reasoning implementation planning for complex, ambiguous, or multi-step tasks by spawning a native subagent running Gemini 3.7 High (`Gemini 3.7 Flash (High)`).

Unlike `_plan-with-ai-os` (which dispatches out-of-band via Perplexity and requires a GitHub remote connector), this skill executes locally with direct workspace filesystem access, eliminating the need for GitHub sync, staging, or remote pushes.

---

## Workflow Steps

### 1. Sanity Check & Scope Formulation
- Identify the target project root, active workspace files, and the user's core requirements.
- Direct local filesystem access is used (no GitHub remote check or push required).

### 2. Spawn Native Subagent for Planning
- Spawn a dedicated subagent configured with `Gemini 3.7 Flash (High)` reasoning.
- Pass a structured planning prompt instructing the subagent to:
  1. Inspect `AG_CONTEXT.md`, `DEVELOPMENT_JOURNAL.md`, and relevant codebase files directly.
  2. Perform root cause analysis and explore edge cases.
  3. Produce a structured implementation plan with:
     - **Goal Description**
     - **User Review Required** (`> [!IMPORTANT]`, `> [!WARNING]`)
     - **Open Questions**
     - **Proposed Changes** (`[MODIFY]`, `[NEW]`, `[DELETE]`)
     - **Verification Plan** (automated tests and manual checks)
  4. Write the plan to `<appDataDir>/brain/<conversation-id>/implementation_plan.md`.

### 3. Present Plan for Approval
- Set `user_facing: true` and `request_feedback: true` on `implementation_plan.md`.
- Await user approval before proceeding to implementation.
