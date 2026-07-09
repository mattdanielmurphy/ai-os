## Goal
Archive features that are only relevant to the legacy Tauri GUI (which is not in active development) into `.devtool/features/archive` to keep the Kanban board clean, and rename the remaining active feature files and internal titles so they are concise and readable.

## User Feedback & Decisions
- Put the legacy features in `.devtool/features/archive`.
- Rename the active features to have better, more concise titles.

## Changes Made
- Created the `.devtool/features/archive` directory.
- Moved 18 legacy Tauri GUI related feature markdown files from `.devtool/features` to `.devtool/features/archive`.
- Renamed 7 active feature files in `.devtool/features` to use short, kebab-case names.
- Updated the YAML frontmatter ID and `# ` title header in each renamed feature file to match the new concise titles:
  - `add-a-kanban-view-...` -> `kanban-todo-sync.md` (Title: `Kanban Todo Sync`)
  - `for-git-commits-in-particular-...` -> `auto-git-commits.md` (Title: `Automated Git Commits`)
  - `help-the-main-smart-agent-...` -> `optimize-agent-menial-tasks.md` (Title: `Optimize Agent Menial Tasks`)
  - `i-think-another-menial-task-...` -> `optimize-agent-log-searching.md` (Title: `Optimize Agent Log Searching`)
  - `project-has-gotten-too-big-...` -> `separate-code-and-notes-context.md` (Title: `Separate Code and Notes Context`)
  - `rules-were-not-transferred-...` -> `sync-rules-to-gemini-md.md` (Title: `Sync Rules to GEMINI.md`)
  - `show-a-message-when-we-run-...` -> `show-quota-limit-message.md` (Title: `Show Quota Limit Message`)

## What Worked
- Relocating legacy features hid them from the Kanban board correctly.
- Renaming the active features simplified the board view, making files easily searchable and cards clean.

## What Didn't Work / Known Issues
None.

## Architecture Notes
Keeping feature filenames and headers concise prevents visual clutter on the Kanban board and improves repository context scans.
