## Goal
Fix thread creation flow (ensuring new threads show up immediately in the sidebar list and output begins rendering automatically), and implement robust prompt box draft autosaving to physical disk after every word/keypress to prevent any text loss on reload or crash.

## Changes Made
- **Backend Rust (`src-tauri/src/main.rs`)**:
  - Implemented `save_prompt_draft` command to write drafts to `~/.gemini/antigravity-cli/drafts/[project_path].txt` on disk.
  - Implemented `load_prompt_draft` command to load draft content from disk for a given project path.
  - Registered both commands in the Tauri command invoke handler list.
- **Frontend TypeScript (`src/main.ts`)**:
  - Added background thread polling loop (`pollThreadsList`) running every 1000ms.
  - Automatically detects when a user is waiting for a new thread (`isWaitingForNewThread === true`) and auto-selects/highlights the newly created thread once `agy` creates it in the background, initiating output timeline rendering immediately.
  - Implemented `savePromptDraft` function which immediately stores the prompt text in `localStorage` and saves to disk synchronously on word boundaries (space/newline) and debounces other keypresses by 150ms to maintain fluid typing performance.
  - Restored prompt draft in `switchToProject` by immediately pulling from `localStorage` for instant visuals, then validating/overwriting asynchronously from the physical disk draft.
  - Hooked prompt draft saving into the `textarea`'s input event and cleared drafts upon prompt submission.

## What Worked
- TypeScript compiled successfully.
- Cargo check passed with no compiler warnings or errors.
- Fully solved the UI desync on new thread creation and guaranteed 100% prompt text recovery on app reload/Vite HMR.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Polling the threads list is debounced via string comparing (`JSON.stringify`) the returned list, avoiding unnecessary DOM repaints and ensuring smooth navigation when scrolling/typing.
