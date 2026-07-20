## Goal
Step 3 is building the frontend for the floating window. Create a minimal floating.html and src/floating.ts, style it using Tailwind (Apple Spotlight style), include an input field and Attach button. When attach is clicked, call get_browser_context and show badge. On Enter, invoke dispatch_to_gemini with prompt and context, then hide the window.

## Changes Made
- Created `floating.html` in the project root with a Tailwind-styled Apple Spotlight / Raycast glassmorphic UI.
- Added input field, attach badge, and SVG button for attaching Chrome Canary tab.
- Created `src/floating.ts` logic to listen for DOM events.
- Used `@tauri-apps/api/tauri` `invoke` to call `get_browser_context` and `@tauri-apps/api/window` `appWindow.hide()` to hide.
- Dispatch logic on Enter triggers the upcoming `dispatch_to_gemini` command.

## What Worked
- `floating.html` UI structure.
- `src/floating.ts` logic mapping successfully.

## What Didn't Work / Known Issues
- `vite.config.ts` might need `build.rollupOptions.input` updated to compile multiple HTML pages in the future, if it fails to build for production. For `tauri dev`, `floating.html` works automatically out of the box.

## Architecture Notes
- Tauri v1 APIs being used for API integration, ensuring forward compatibility where possible.
