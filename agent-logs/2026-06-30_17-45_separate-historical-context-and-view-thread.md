## Goal
Improve the historical context handling by:
1. Separating the "Historical Context" block from the user's active message in the markdown UI timeline.
2. Increasing truncation limits for context histories to prevent early cutoff.
3. Providing a CLI utility `view-thread` for agents to read the complete, untruncated steps of any thread.

## Changes Made
- **[scripts/view_thread.py](file:///Users/matthewmurphy/projects/ai-os/scripts/view_thread.py)**: Created a Python command-line tool that parses thread log JSONL files, resolves partial UUIDs, and outputs untruncated conversation steps. Supports `--step <index>` and `--last <N>` flags.
- **[package.json](file:///Users/matthewmurphy/projects/ai-os/package.json)**: Added a `"view-thread"` run script pointing to `scripts/view_thread.py`.
- **[src/main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts)**:
  - Updated `getCompactifiedContext` to retain up to 15 conversation steps (was 6) and 2500 characters per message (was 300) to keep useful content intact.
  - Injected the active Thread ID and a system directive showing how to run `pnpm run view-thread <thread_id>` inside the `combinedPrompt`.
  - Modified `buildTimelineHtml` to parse out historical context and thread ID from resumed prompts, rendering them as a beautifully styled, collapsible `<details>` card on the left side of the timeline, distinct from the user's message bubble on the right.
- **[FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md)** & **[AG_CONTEXT.md](file:///Users/matthewmurphy/projects/ai-os/AG_CONTEXT.md)**: Updated features ledger and architectural context.

## What Worked
- Separating historical context using regex and string indices in `buildTimelineHtml` successfully isolated historical notes from the main user message bubble.
- Collapsible cards render beautifully in light and dark modes.
- `view_thread.py` prints clean, step-by-step transcript logs for the agent.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Continuing threads uses `/clear` followed by a combined prompt. By structuring the combined prompt with fixed markers (`Continuing conversation from history (Thread ID: ...)`, `[SYSTEM DIRECTIVE: ...]`, `Historical Context:\n`, and `User request:`), we keep backend-side context clean while allowing the frontend parsing parser to separate historical records from current queries.
