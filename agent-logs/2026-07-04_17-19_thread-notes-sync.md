## Goal
Add "thread notes" sync capability so that users can view and check off thread-specific todos from an Obsidian markdown file directly in the AI-OS UI.

## Changes Made
1. **`src-tauri/src/main.rs`**: Added `read_thread_notes_file` and `write_thread_notes_file` endpoints to allow reading and writing to `/Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/thread-notes.md`.
2. **`index.html`**: Added a new right sidebar for "Thread Notes & Todos".
3. **`src/threadNotes.ts`**: Created a manager and renderer that parses the markdown file for project/thread headings (`# Project`, `## ThreadId`) and lists `- [ ]` / `- [x]` todos, rendering them as interactive checkboxes.
4. **`src/main.ts`**: Hooked `renderThreadNotesSidebar` into all places where `activeThreadId` is changed, ensuring the sidebar stays synchronized with the active thread.

## What Worked
- Tauri backend properly serves the fixed-path markdown file.
- The UI handles reading, rendering, and toggling checkboxes which seamlessly rewrites the markdown lines.
- Compilation passes via `pnpm tsc --noEmit`.

## What Didn't Work / Known Issues
- Initializing notes for a thread relies on a manual click "Initialize Thread Notes" if none exist yet, which keeps the markdown clean until the user explicitly wants to track a thread.

## Architecture Notes
- The architecture was strictly followed by decoupling the logic into a new UI file (`threadNotes.ts`) and relying on Tauri `invoke` commands instead of injecting complex rust parsing. The file I/O operations directly mutate the Obsidian vault without intermediate caching to ensure it's a single source of truth.
