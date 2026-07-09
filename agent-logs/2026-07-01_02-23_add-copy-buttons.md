## Goal
Add a copy button to each final response from the AI, user prompt messages, and a separate copy button to code blocks.

## Changes Made
- Modified `src/main.ts` to add a custom renderer for `marked` to intercept code blocks and inject a custom `div` container with a copy button.
- Modified `src/main.ts` rendering logic for `user_input` and `planner_response` blocks to add a hovering absolute-positioned copy button.
- Used `encodeURIComponent` and `decodeURIComponent` along with `data-content` HTML attributes to safely store markdown block content and execute `navigator.clipboard.writeText()` without syntax errors.

## What Worked
- Confirmed that the UI successfully renders copy buttons that show up on hover for AI responses, user messages, and code blocks.
- Tested `pnpm tsc` and it compiled correctly without any issues.

## What Didn't Work / Known Issues
- N/A

## Architecture Notes
- The chat TUI parser operates directly on JSONL files and parses individual steps into HTML inside `buildTimelineHtml`.
- `marked.use({ renderer })` is required for customizing the HTML output of code blocks in newer versions of the `marked` library.
