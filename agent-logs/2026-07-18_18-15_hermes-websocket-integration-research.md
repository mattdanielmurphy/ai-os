# Hermes WebSocket Integration Research

## Goal
Replace the PTY/tmux/xterm.js approach for the Hermes agent engine in the ai-os Tauri app with a WebSocket JSON-RPC connection to `hermes serve`. Keep agy and Claude on xterm.js unchanged.

## Protocol Discovered

**Endpoint**: `ws://127.0.0.1:PORT/api/ws` (existing server on port 9119)
**Protocol**: Newline-delimited JSON-RPC 2.0

### RPC calls (client → server)
- `session.create({ cwd, source, model?, provider?, cols })` → `{ session_id, info, stored_session_id? }`
- `session.close({ session_id })`
- `session.interrupt({ session_id })`
- `prompt.submit({ session_id, text, image? })` — fire-and-forget, response via events
- `session.list()`, `session.resume()`, etc.

### Server events (server → client)
- `gateway.ready` — on connect
- `session.info` — metadata
- `message.start` / `message.delta` / `message.complete` — streaming response
- `thinking.delta` / `reasoning.delta` — thinking tokens
- `tool.start` / `tool.progress` / `tool.complete` — tool calls
- `clarify.request` / `approval.request` — user interaction
- `error`

### Reference implementation
Desktop app uses `JsonRpcGatewayClient` (extends `WebSocket`) → `HermesGateway` in `apps/desktop/src/hermes.ts`
Core protocol handler: `apps/shared/src/json-rpc-gateway.ts`

## Current Architecture (to keep for agy/claude)

**Rust** (`tauri-gui/src-tauri/src/main.rs`):
- `spawn_single_pty()` spawns `hermes`/`claude`/`agy` via `portable_pty`
- Reader thread → `pty-output` Tauri event
- `write_to_pty()` / `resize_pty()` for bidirectional I/O
- tmux wrapper optional

**Frontend** (`tauri-gui/src/main.ts`):
- Single shared xterm.js Terminal for engine output
- `currentEngine: "claude" | "agy" | "hermes"` selects buffer/PTY
- `listen("pty-output")` → cached buffers → `term.write()`
- Per-engine buffers: `claudeBuffers`, `agyBuffers`, `hermesBuffers`

## Target Architecture

### Strategy: two rendering paths
- **agy/claude**: Keep PTY + xterm.js as-is
- **hermes**: Connect to `ws://127.0.0.1:9119/api/ws` → custom chat UI

### Rust changes needed
1. Add `hermes_serve_port: u16` to `ProjectSession` (default 9119)
2. When engine == "hermes", skip `spawn_single_pty` — just store port
3. Return port info in `switch_active_project` response
4. No PTY reader/writer for Hermes engine

### Frontend changes needed
1. When `currentEngine === "hermes"`, hide xterm.js, show chat message list
2. Connect WebSocket to `ws://127.0.0.1:9119/api/ws` on engine switch
3. `session.create()` on first connect
4. `prompt.submit()` from textarea instead of PTY write
5. Render events → streaming text, thinking blocks, tool cards
6. Keep agy/claude on xterm.js unchanged
