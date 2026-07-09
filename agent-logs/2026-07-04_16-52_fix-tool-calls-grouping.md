## Goal
The user reported a regression in the UI where tool calls were being rendered in separate boxes (one box per tool call, followed by another box with more tool calls) instead of a single grouped box that expands until the agent finishes its work cycle.

## Changes Made
- Modified `src/main.ts` `buildTimelineHtml` function.
- Changed the rendering approach from a flat list of `blocks` to a structured list of `turns`.
- Each "turn" begins with a user input and collects all subsequent agent text responses (`planner_response`) and tool calls/thoughts into a single turn object.
- Aggregated all `tool_calls` and `thought` blocks inside a turn into a single unified `tool-call-group` box.
- Ensured the tool calls box opens correctly for the last turn while the agent is thinking.
- Re-rendered text responses strictly below the unified tool calls box for that turn.

## What Worked
- Confirmed TypeScript compilation passed and the code groups all agent output correctly per user turn.

## What Didn't Work / Known Issues
- By grouping all tool calls together, the UI technically loses the exact chronological interleaving of text responses versus tool calls (all tool calls now appear at the top of the turn before the text responses). However, this perfectly aligns with the user's requested specification ("They should be in ONE box").

## Architecture Notes
- The log parser (`renderCustomTuiLog`) extracts JSON objects line-by-line and feeds them as `Step` objects to `buildTimelineHtml`. Grouping them dynamically during HTML generation proved more robust than changing the line-by-line state extraction.
