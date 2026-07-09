## Goal
Archive features that are only relevant to the legacy Tauri GUI (which is not in active development) into `.devtool/features/archive` to keep the Kanban board clean.

## User Feedback & Decisions
Put the legacy features in `.devtool/features/archive`.

## Changes Made
- Created the `.devtool/features/archive` directory.
- Moved 18 legacy Tauri GUI related feature markdown files from `.devtool/features` to `.devtool/features/archive`.

## What Worked
All target files were successfully relocated, leaving only general/VSCode features in the main `.devtool/features` directory.

## What Didn't Work / Known Issues
None.

## Architecture Notes
Moving these task card files to a subdirectory hides them from the flat list rendering of the `vscode-agent-kanban` extension, thereby filtering out legacy items from the Kanban board.
