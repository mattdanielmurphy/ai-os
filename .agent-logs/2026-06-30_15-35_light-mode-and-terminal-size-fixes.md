## Goal
1. Fix light mode legibility issues:
   - Markdown strong text and headings should not be forced white.
   - Code snippets should be highly visible in light mode (e.g. blue text on light background).
   - Lay out steps as a clean timeline with right-aligned user messages and left-aligned agent responses/steps, with a strict max-width of 65ch. Remove repetitive "Assistant Response" headers/robot emojis.
2. Fix all-black terminal display error when expanding the terminal container.
3. Support a three-state terminal height: collapsed (64px), intermediate (320px) when typing slash commands (e.g. starting with `/`), and expanded (full-screen).
4. Enhance sidebar project/thread items for light mode:
   - Hover contrast.
   - Indented threads panel border and button colors.
   - Threads list container height increased to 2x (max-h-96).
   - Compact thread items (omit long UUID, show truncated hex hashes, clamp snippets to 1 line, high-contrast date strings).

## Changes Made
- **index.html**: Removed heavy-handed prose classes from `#markdown-preview-pane` wrapper to avoid styling timeline elements like headings and strong text globally.
- **src/styles.css**: Appended custom CSS overrides for `.prose code` and `.prose pre` to style code snippets beautifully with dynamic colors under `.dark` and light mode styles.
- **src/main.ts**:
  - Refactored `renderCustomTuiLog` to render user inputs as right-aligned gray bubbles and assistant/tool responses as left-aligned blocks, with a maximum width of `65ch`.
  - Added `renderHistoricalThreadLog` to render past thread logs using the exact same beautiful chat-bubble layout.
  - Made `isTuiExpanded` global, enabling key/input handlers to inspect it.
  - Updated `term.onData` and `textarea` input event listeners to check for lines/inputs starting with `/`. If detected and terminal is collapsed, it expands the terminal container to `320px` (intermediate size) to display autocomplete suggestions, and collapses back to `64px` when cleared.
  - Fixed terminal expansion display glitch by triggering `resizePty()` at multiple timeouts (50ms, 150ms, 320ms) to ensure fitting happens smoothly as height transition completes.
  - Improved active project tabs and hover highlights to match light mode cleanly.
  - Shortened UUIDs to 8-character hashes (`#a8f8211b`), increased max-height of threads list to `max-h-96`, clamped snippet summaries to a single line, and boosted contrast of dates.
- **FEATURES.md**: Documented these UX, styling, and sizing enhancements.

## What Worked
- TypeScript compiles perfectly and Vite built successfully.
- Code blocks are highly readable in both light and dark modes.
- Terminal heights dynamically adjust on `/` key presses and text changes.
- Layout rendering for logs and history is unified and clean.

## What Didn't Work / Known Issues
- None.
