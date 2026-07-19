## Goal
Fix the remaining issues of the Hermes websocket integration:
1. Fix the duplicate `appendHermesUserMessage` implementation in `tauri-gui/src/main.ts` which broke compilation.
2. Fix the `addHermesThinkingBlock` TypeScript error where `block` was possibly null.
3. Fix the runtime issue where assistant message container creation was missing from `onMessageStart` callback.

## Changes Made
- Modified [main.ts](file:///Users/matt/projects/ai-os/tauri-gui/src/main.ts):
  - Removed duplicate `appendHermesUserMessage` function.
  - Refactored `addHermesThinkingBlock` to guarantee `block` is non-null when querying the thinking body and avoid typescript compilation warnings.
  - Updated `hermesChat.onMessageStart` to create and append the assistant message bubble to the DOM (`#hermes-messages`) on the start of a message event.
- Modified [housekeep.py](file:///Users/matt/projects/ai-os/scripts/housekeep.py) to look for transcripts inside the `/Users/matt/.gemini/antigravity/` directory.
- Updated status to `review` in [.devtool/features/hermes-agent-gui-integration.md](file:///Users/matt/projects/ai-os/.devtool/features/hermes-agent-gui-integration.md).

## What Worked
- Vite/TypeScript build runs successfully with zero errors.
- Both duplicate function error and "possibly null" errors are resolved.
- Assistant message bubble is now created on the WebSocket `message.start` event.

## What Didn't Work / Known Issues
- None so far.

## Architecture Notes
- The websocket interface allows the custom chat UI to directly interact with `hermes serve` at port 9119, avoiding the flaky PTY tmux xterm wrapper.
- All events (`message.start`, `message.delta`, `message.complete`, `thinking.delta`, `tool.start`, `tool.complete`) are mapped to the correct DOM handlers, creating a clean web interface stream.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/babeed95-d864-4a7b-a360-606d433900f3/.system_generated/logs/transcript.jsonl)
