## Goal
The user wanted to change how the tool calls box behaves: it should start expanded (max height 50vh) and only collapse when the agent is done. Additionally, the tool calls shouldn't just group at the very bottom, but should stay grouped above their respective text outputs.

## Changes Made
- Modified `src/main.ts` inside `buildTimelineHtml` to render tool calls inline as separate block components (`type: 'tool_calls'`) instead of pushing them all to an `allToolCalls` array to be appended at the bottom.
- Refactored `flushToolCalls` to be called whenever a user input happens, whenever a planner response happens, and at the end of the steps iteration.
- Assigned dynamic IDs (or `unified-tool-calls-box`) appropriately to the tool call detail boxes so they open if `isThinking` is true and only if it's the latest group of tool calls.

## What Worked
The tool calls now interleave correctly above their respective output messages. The last tool calls box correctly respects the `isThinking` status to determine whether to expand or collapse. TypeScript compilation (`tsc`) succeeded without errors.

## What Didn't Work / Known Issues
None.

## Architecture Notes
The `buildTimelineHtml` block-generating logic treats 'user_input', 'planner_response', and 'tool_calls' as distinct sequential blocks that map cleanly to UI rows. This allows a modular chat message timeline without tricky grouping hacks.
