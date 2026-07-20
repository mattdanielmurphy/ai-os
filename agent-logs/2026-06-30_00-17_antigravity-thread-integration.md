## Goal
Integrate actual Antigravity thread history (brain folder transcripts) per project directory, support context-pruned thread resumption via `/resume` and `/clear` with compact transcript summaries, enable new thread creation, render transcripts as chat threads in the Output Preview Pane, and style all scrollbars globally to match macOS auto-hiding scrollbars.

## Changes Made
1. **`src-tauri/src/main.rs`**: Updated `get_project_threads` command to:
   - Scan files in the global Antigravity brain directory (`~/.gemini/antigravity-cli/brain`).
   - Match and extract the canonical project path from the first 128KB of transcripts to group threads correctly.
   - Parse the first `USER_INPUT` prompt dynamically from JSON lines as the thread's title and snippet.
2. **`index.html`**: Added a `new-thread-btn` "+" button next to "Project Threads" header in the sidebar.
3. **`src/main.ts`**:
   - Declared global module-level variables `activeThreadId` and `activeThreadContext`.
   - Updated `switchToProject` to clear thread state to avoid cross-project pollution.
   - Built helpers `formatTranscriptToMarkdown` (renders JSONL dialogue as formatted User/Assistant Markdown text blocks) and `getCompactifiedContext` (extracts brief prompts and replies with code blocks omitted to limit token usage).
   - In `renderProjectThreads`, highlighted the selected thread and configured click triggers to run `switch_active_project`, wait if a new session boots, send `/resume <thread_id>`, and set context.
   - Added `new-thread-btn` click handler to clear thread states, reset the preview, switch active engine to `agy`, and run `/clear\r`.
   - Updated prompt input intercepts to clear context and send compact context before the user's message when continuing a thread.
4. **`src/styles.css`**: Configured custom scrollbars globally (`*`). Thumbs are transparent by default and fade in as macOS pill scrollbars when hovered (`*:hover::-webkit-scrollbar-thumb`).
5. **`FEATURES.md`**: Updated confirmed ledger with the new thread integration and scrollbar improvements.

## What Worked
- Substring path matches successfully map and group threads.
- Chat logs are parsed dynamically from JSON lines to a clean markdown presentation.
- Global scrollbars display with the correct dimensions and styling inside the webview.

## What Didn't Work / Known Issues
- Large transcripts may be truncated when verifying path mappings, but 128KB is large enough to cover the initial workspace declaration lines of any conversation transcript.

## Architecture Notes
- Antigravity stores transcripts in `~/.gemini/antigravity-cli/brain/<uuid>/.system_generated/logs/transcript.jsonl`.
- Resuming a thread via `/resume <id>` must be accompanied by `/clear` and compact context feeding to preserve context continuity without token inflation.
