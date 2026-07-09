## Goal
Improve the UI of the tool calls box by adding borders around each tool call, using a table layout for parameter/value alignment, and correctly rendering escaped `\n` characters in multiline string arguments so they are actually readable.

## Changes Made
- Modified `src/main.ts` inside the `renderToolCallHtml` function.
- Converted the flexible div-based list of arguments into a `<table>` with `table-layout: fixed`. The keys column is set to `width: 120px` to enforce alignment, while the value column gets the remaining width.
- Added logic to check string arguments for literal `\\n` sequences and replace them with actual `\n` characters so that `marked.parse` properly renders them as multiline code blocks instead of a single unreadable line.
- Added inline styles for a border (`1px solid rgba(128, 128, 128, 0.2)`), border-radius, and a subtle background to `.unified-tool-call-row` so each tool call is clearly separated visually.

## What Worked
The tool calls now render individually bounded by borders. Parameters align cleanly via the table layout. Multiline text strings that had escaped newlines are properly parsed and expanded into their multiline visual equivalents.

## What Didn't Work / Known Issues
None.

## Architecture Notes
The TUI generates HTML dynamically from the raw JSON log stream by intercepting the `steps` array. Modifying how properties (like multiline strings) are sanitized or passed to `marked` must be done cautiously to ensure valid JSON isn't improperly malformed before rendering.
