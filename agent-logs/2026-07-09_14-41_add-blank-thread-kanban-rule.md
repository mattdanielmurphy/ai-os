## Goal
Add a rule instructing agents that start in a blank thread to automatically locate matching Kanban features and move them to "In Progress", or create a new Kanban feature if none matches.

## User Feedback & Decisions
Configure the rule to:
- Check for existing matching features and mark them `status: "in-progress"`.
- If no match, create a new feature file with a good title, a unique `id`, and an objective description of the user request.
- Prefix bug fixes with "Bug: ".

## Changes Made
- Added the "Blank Thread / Task Selection Rule" to [.agents/AGENTS.md](file:///Users/matt/projects/ai-os/.agents/AGENTS.md).
- Synchronized the same workspace rule to [CLAUDE.md](file:///Users/matt/projects/ai-os/CLAUDE.md) inside `<WORKSPACE_RULES>`.

## What Worked
The rule was added seamlessly to both the workspace and Claude system rules templates, ensuring future agents will dynamically check and update the Kanban cards.

## What Didn't Work / Known Issues
None.

## Architecture Notes
By making this a system-level constraint, agents running under the CLI will natively interface with the markdown-based Kanban files at the start of any new session/thread.
