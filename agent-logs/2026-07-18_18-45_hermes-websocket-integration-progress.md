# Goal: Replace Hermes PTY/Tmux with WebSocket JSON-RPC

## The Problem
Hermes Agent runs inside a `portable_pty` (wrapped in tmux) rendered in xterm.js inside the Tauri webview. This is glitchy — sizing issues, paste problems, broken link clicks, unreliable loading. agy and Claude Code keep the PTY path; only Hermes changes.

## Architecture
**Before:**
```
Tauri webview → xterm.js → portable_pty → tmux → hermes (prompt_toolkit REPL)
```

**After:**
```
Tauri webview → custom chat UI → WebSocket → hermes serve (headless JSON-RPC server, already running on port 9119)
```

## What's Been Done

### 1. Research (agent-logs/2026-07-18_18-15_hermes-websocket-integration-research.md)
- Mapped the Hermes serve JSON-RPC protocol (WebSocket at `ws://127.0.0.1:9119/api/ws`, newline-delimited JSON-RPC 2.0)
- Identified RPC methods: `session.create`, `session.close`, `prompt.submit`, `session.interrupt`
- Identified events: `gateway.ready`, `session.info`, `message.start`, `message.delta`, `message.complete`, `thinking.delta`, `reasoning.delta`, `tool.start`, `tool.complete`, `error`
- Found the Hermes desktop app's reference implementation: `JsonRpcGatewayClient` in `apps/shared/src/json-rpc-gateway.ts`

### 2. Rust Backend Changes (tauri-gui/src-tauri/src/main.rs)
- Added `hermes_ws_port: u16` to `SwitchResult` struct (line 828)
- Modified `ensure_engine_pty()` to return `(u32, bool, u16)` — returns `(0, false, 9119)` for Hermes (skips PTY spawn entirely)
- Modified `switch_active_project()`:
  - When engine=="hermes" and new project: skips PTY spawn, only spawns mini shell, returns `hermes_ws_port: 9119`
  - When engine=="hermes" and existing project: `ensure_engine_pty` returns immediately with port 9119
  - Destructures the new `hermes_ws_port` from the return value
  - Passes `hermes_ws_port` through all `SwitchResult` constructions
- Modified `write_to_pty()`: returns `Ok(())` immediately if `terminal_type == "hermes"` (no-op)
- Removed `hermes` from the PTY writer routing in `write_to_pty()`

### 3. HTML (tauri-gui/index.html)
- Added `<div id="hermes-chat-container">` after `#terminal-container` (line 191-207)
- Contains `#hermes-messages` div with a welcome message
- Hidden by default (`style="display: none"`) — shown when engine is "hermes"

### 4. CSS (tauri-gui/src/styles.scss)
- Added full styling for `.hermes-chat-container`, `.hermes-message`, `.hermes-thinking-block`, `.hermes-tool-call`, `.hermes-error`, `.hermes-connection-status`
- Includes animations: `hermes-message-in` (fade+slide), `hermes-blink` (cursor blink)
- Message bubbles for user (right-aligned, primary color) and assistant (left-aligned)
- Collapsible thinking blocks, expandable tool call results

### 5. TypeScript WebSocket Client (tauri-gui/src/hermesChat.ts)
- `HermesChatClient` class — full JSON-RPC 2.0 WebSocket client
- Methods: `connect()`, `disconnect()`, `createSession()`, `submitPrompt()`, `closeSession()`, `interrupt()`
- Event callbacks: `onMessageStart`, `onMessageDelta`, `onMessageComplete`, `onThinkingDelta`, `onReasoningDelta`, `onToolStart`, `onToolComplete`, `onError`
- Connects to `ws://127.0.0.1:9119/api/ws`
- Pending request tracking with timeout
- Handles server events via `handleEvent()` method

### 6. Frontend Wiring (tauri-gui/src/main.ts)
- Imported `HermesChatClient` from `./hermesChat`
- Instantiated `hermesChat` global variable
- Added helper functions: `initHermesChat()`, `showHermesChatUI()`, `appendHermesUserMessage()`, `updateHermesMessageContent()`, `finalizeHermesMessage()`, `addHermesThinkingBlock()`, `addHermesToolCall()`, `completeHermesToolCall()`, `addHermesError()`, `escapeHtml()`
- Updated engine radio change handler:
  - When switching TO "hermes": shows chat UI, wires event callbacks
  - When switching FROM "hermes": hides chat UI, closes session, disconnects WebSocket
- Updated Enter key handler (line 3588-3610):
  - When `currentEngine === "hermes"`: sends via WebSocket `prompt.submit` instead of PTY write
  - Falls back to PTY write if WebSocket not connected
- Updated `invoke<SwitchResult>` type signature to include `hermes_ws_port`

## What's Left To Do

### Blocking Issues (Build Fails)
1. **`tsc` build error**: Line 3215 — `block` is possibly null (the `as HTMLElement | null` cast + `block!.querySelector` non-null assertion isn't satisfying TS). Need to fix the `addHermesThinkingBlock` function.
2. **`tsc` build error**: Line 3289 — `Cannot find name 'updateHermesMessageContent'`. This is a stale LSP error — the function IS defined at line 3200. But the build may fail on this. Need to verify.
3. **`tsc` error in hermesChat.ts**: `HermesToolCall` interface is declared but unused. Need to remove it.

### Runtime Issues to Fix
4. **Session ID generation**: The `onMessageStart` handler uses the server-provided `msgId` directly, but `onMessageDelta` and `onMessageComplete` use `hermesCurrentMessageId` which is set from that same `msgId`. The issue is that the first `message.delta` event might arrive before `message.start` if the server sends them in the same WebSocket frame. The `handleEvent` method processes events in order, so this should be fine — but if the server drops `message.start`, the UI won't create a message container for the deltas.

5. **No `message.start` event from server**: The Hermes server might not emit `message.start` — it might just start with `message.delta`. We need to test this. If it doesn't, we need to handle the first `message.delta` by creating a message container. The current code in `hermesChat.ts` `handleEvent` always fires `onMessageStart` for `message.start` events, but if none come, we need to create the message on first delta.

6. **No assistant message container creation**: Currently, when `onMessageStart` fires, it sets `hermesCurrentMessageId = msgId` — but it doesn't create a DOM element for the message. The DOM element is never created! We need `onMessageStart` to ALSO create the message bubble in the DOM. The `appendHermesAssistantMessage()` function was written for this purpose but was removed because it was "unused" after I mistakenly changed the handler to just use `msgId` directly. **This is the critical bug** — the assistant message bubbles never appear in the UI.

### Fix for #6
The `onMessageStart` handler should be:
```typescript
hermesChat.onMessageStart = (msgId) => {
    hermesCurrentMessageId = msgId
    // Create the message bubble in the DOM
    const msgsEl = document.getElementById("hermes-messages")
    if (!msgsEl) return
    const welcome = msgsEl.querySelector(".hermes-welcome")
    if (welcome) welcome.remove()
    const div = document.createElement("div")
    div.className = "hermes-message hermes-message-assistant"
    div.id = msgId
    div.innerHTML = `<div class="hermes-message-role">Hermes</div><div class="hermes-message-content"><span class="hermes-streaming-cursor"></span></div>`
    msgsEl.appendChild(div)
    msgsEl.scrollTop = msgsEl.scrollHeight
}
```

### Verification
7. Build: `cd /Users/matt/projects/ai-os/tauri-gui && bun run build`
8. Test: Switch to Hermes engine in the Tauri app, send a prompt, verify WebSocket connects, verify messages appear
9. Verify the Hermes server is still running: `lsof -i :9119`

## Key Files
- `/Users/matt/projects/ai-os/tauri-gui/src-tauri/src/main.rs` — Rust backend
- `/Users/matt/projects/ai-os/tauri-gui/index.html` — HTML
- `/Users/matt/projects/ai-os/tauri-gui/src/styles.scss` — CSS
- `/Users/matt/projects/ai-os/tauri-gui/src/hermesChat.ts` — WebSocket client
- `/Users/matt/projects/ai-os/tauri-gui/src/main.ts` — Frontend wiring

## Constraints
- agy and Claude Code PTY/xterm.js paths must NOT be touched
- No new npm packages — use native WebSocket API
- Hermes server is already running on port 9119 (verify with `lsof -i :9119`)
- The `prepare_spare_engine` function in main.rs still spawns `hermes` via PTY for the spare engine — this should be updated to skip Hermes too
- The session eviction code in `switch_active_project` still tries to kill `hermes_pid` — this is harmless since the PID is always 0