---
name: plan-multi-step
description: Creates a multi-step plan folder under plans/<plan-name>/ with numerical step markdown files (e.g., 01-*.md, 02-*.md) and initial status.json for execution with /build.
---

# Multi-Step Plan Creator Skill (`/plan-multi-step`)

Use this skill when the user requests creating a multi-step plan structure for execution with `/build`.

## Workflow & Structure

1. **Choose a Plan Slug/Name:**
   - Create a clean slug for the feature or task (e.g., `model-override-proxy` or `auth-refactor`).
   - Create directory `plans/<plan-name>/` at the project root.

2. **Generate Step Markdown Files:**
   - Break down the implementation into discrete, ordered step files (e.g. `01-setup.md`, `02-core-logic.md`, `03-tests.md`).
   - Each markdown step file should contain:
     - Clear step objective and title
     - Relevant file paths to create/modify
     - Precise instructions, code snippets, or verification steps for that specific step.

3. **Initialize `status.json`:**
   - In `plans/<plan-name>/status.json`, initialize the state tracker:
   ```json
   {
     "plan_name": "<plan-name>",
     "status": "IN_PROGRESS",
     "current_step": 1,
     "steps": [
       {
         "id": 1,
         "file": "01-setup.md",
         "title": "Initial Setup & Config",
         "status": "TODO"
       },
       {
         "id": 2,
         "file": "02-core-logic.md",
         "title": "Core Implementation",
         "status": "TODO"
       }
     ]
   }
   ```

4. **Integration with `/build`:**
   - Once `plans/<plan-name>/` is created, inform the user that the plan is ready.
   - The user (or agent) can now run `/build` to execute each step sequentially.
