## Goal
Establish a clean, simple project planning and global task tracking structure across the local files and the Obsidian vault, reorganize the `ai-os` docs, and configure system rules so future agents automatically respect this system.

## User Feedback & Decisions
*   The user preferred a markdown-based approach for the task tracking system over heavier solutions like Notion.
*   Agreed to keep early-stage planning and general roadmaps in the iCloud Obsidian vault (`Development/Project Notes/`) to keep the primary code repositories clean.
*   Decided the active UI direction for `ai-os` will be a custom Tauri desktop app containing Markdown/Monaco editors and a Kanban board.

## Changes Made
*   Reorganized `docs/` in `ai-os` into `docs/active/` and `docs/archive/` and swept out deprecated files.
*   Created `/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/Development/Project Notes/` if it wasn't present.
*   Created `Project Index.md` and `Global Todos.md` under Obsidian project notes.
*   Created a Safari userscript migration/CORS troubleshooting note `gemini-thread-sync.md` in Obsidian.
*   Added Obsidian Project Notes and Global Todos rules/metadata schemas to the master workspace rules in [AGENTS.md](file:///Users/matt/projects/ai-os/AGENTS.md) and [CLAUDE.md](file:///Users/matt/projects/ai-os/CLAUDE.md).

## What Worked
*   Organizing the `docs/` folder makes active designs immediately scannable.
*   The plain-text markdown todo format allows future agents to filter tasks using standard regex.

## What Didn't Work / Known Issues
*   Initially tried using `write_to_file` with `ArtifactMetadata` on paths outside the artifact workspace directory, which is restricted. Fixed by calling without metadata for Obsidian files.

## Architecture Notes
*   **Global Todos Format**: `- [ ] Description [project:: <id>] [assignee:: user|agent] [due:: YYYY-MM-DD]` under headings (`## To Do`, `## In Progress`, `## Done`) is designed to work seamlessly with both the Obsidian Kanban plugin and agent filesystem scripts.
