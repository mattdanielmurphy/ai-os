## Goal
Fix issues with Kanban task ("feature") management:
1. Stop requesting user approval upon creating feature files.
2. Correct formatting to use a `# Title` header and markdown body description, keeping YAML frontmatter free of `title` and `description` tags.
3. Keep finished features in `status: "review"` under `.devtool/features/` instead of moving them to `done/` or marking them `done`.

## Changes Made
- Modified [.agents/AGENTS.md](file:///Users/matt/projects/ai-os/.agents/AGENTS.md) and [CLAUDE.md](file:///Users/matt/projects/ai-os/CLAUDE.md) to add and update the Kanban task rules ("Blank Thread / Task Selection Rule" and "Task Completion & Review Rule").
- Created new task file [.devtool/features/fix-kanban-task-management.md](file:///Users/matt/projects/ai-os/.devtool/features/fix-kanban-task-management.md) to track this work under `status: "in-progress"`.
- Cleaned up formatting issues in existing feature files:
  - [.devtool/features/done/macos-text-replacements-migration.md](file:///Users/matt/projects/ai-os/.devtool/features/done/macos-text-replacements-migration.md)
  - [.devtool/features/code2prompt-context.md](file:///Users/matt/projects/ai-os/.devtool/features/code2prompt-context.md)

## What Worked
- Programmatic rules update and formatting cleanups.
- Verified task rules have been updated in both files.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- Handled tasks are automatically set to `status: "review"` by `scripts/auto_commit.py` when committing. The new rules specify they should stay in `.devtool/features/` and not be manually renamed or moved to `done/` by the agent.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-ide/brain/8078756b-83f5-4ab6-a44c-576cd449a03e/.system_generated/logs/transcript.jsonl)
