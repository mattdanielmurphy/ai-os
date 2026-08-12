# Hermes Gateway — WebSocket JSON-RPC Protocol

The Hermes `serve` / `dashboard` server exposes a WebSocket endpoint at `ws://127.0.0.1:{port}/api/ws` (default port 9119) using **newline-delimited JSON-RPC 2.0**.

## Wire Format

Each message is a single JSON object terminated by `\n`. Both directions use the same framing.

```json
{"jsonrpc":"2.0","id":1,"method":"session.create","params":{"cols":96,"source":"desktop"}}
```

## Client → Server (RPC Calls)

### Session Lifecycle

| Method | Params | Returns | Notes |
|--------|--------|---------|-------|
| `session.create` | `{ cols, source, cwd?, profile?, model?, provider?, reasoning_effort?, fast? }` | `{ session_id, info, stored_session_id? }` | Creates a new chat session. The `info` object contains runtime metadata (model, provider, etc.). |
| `session.close` | `{ session_id }` | `{ ok }` | Closes a session. |
| `session.interrupt` | `{ session_id }` | `{ ok }` | Interrupts the current response mid-stream. |
| `session.resume` | `{ session_id (or stored_session_id), cols?, source? }` | `{ session_id, info, stored_session_id? }` | Resumes an existing session. |
| `session.list` | `{ limit?, offset?, min_messages?, archived?, order? }` | `{ sessions, total }` | Lists sessions. |
| `session.info` | `{ session_id }` | `{ session_id, title, model, ... }` | Session metadata. |
| `session.compress` | `{ session_id }` | `{ ok }` | Manually triggers context compression. |

### Chat

| Method | Params | Returns | Notes |
|--------|--------|---------|-------|
| `prompt.submit` | `{ session_id, text, image?, attachment?, ... }` | `{ ack }` (immediate) | Fire-and-forget — actual response comes via streaming events. Timeout defaults to 1800s (30 min). |
| `prompt.submit` with `truncate_before_user_ordinal` | `{ session_id, text, truncate_before_user_ordinal: N }` | `{ ack }` | Truncates conversation history back to message N before submitting. Used for retry/edit. |

### Approval & Clarify

| Method | Params | Returns |
|--------|--------|---------|
| `approval.respond` | `{ session_id, request_id, approved: bool }` | `{ ok }` |
| `clarify.respond` | `{ session_id, request_id, response: string }` | `{ ok }` |
| `sudo.respond` | `{ session_id, request_id, password: string }` | `{ ok }` |
| `secret.respond` | `{ session_id, request_id, secret: string }` | `{ ok }` |

### Model & Config

| Method | Params |
|--------|--------|
| `model.change` | `{ session_id, model, provider?, reasoning_effort?, fast? }` |
| `model.info` | `{}` — returns available models, current selection |
| `config.get` | `{ key? }` — returns config (or specific key) |
| `config.set` | `{ key, value }` |

### Tool & Skills

| Method | Notes |
|--------|-------|
| `skills.manage` | Long-running (pooled). Install/search/remove skills. |
| `tools.list` | List available tools and their status. |
| `tools.toggle` | Enable/disable a toolset. |

### Other

| Method | Notes |
|--------|-------|
| `billing.step_up` | Long-running (pooled). Triggers plan upgrade flow. |
| `browser.manage` | Long-running (pooled). Browser CDP management. |
| `complete.path` | Path autocompletion (pooled, can be slow on large repos). |
| `complete.slash` | Slash command autocompletion (pooled). |
| `llm.oneshot` | Single LLM call outside the agent loop (pooled). |
| `process.list` | List running background processes. |
| `shell.exec` | Long-running (pooled). Execute a shell command. |
| `setup.runtime_check` | Check runtime readiness (pooled). |
| `setup.status` | Check if setup is complete (pooled). |
| `plugins.manage` | Plugin management (pooled). |
| `pet.*` | Pet-related operations (pooled, network-heavy). |
| `projects.*` | Project management (pooled). |

## Server → Client (Events)

Events are sent as JSON-RPC requests with `"method": "event"` and the event payload in `params`.

### Core Event Types

```typescript
type GatewayEventName =
  | 'gateway.ready'         // On connect: { session_id?, profile?, skin?, ... }
  | 'session.info'          // Session metadata emitted after create/resume
  | 'message.start'         // Agent began generating a response
  | 'message.delta'         // Streaming token delta: { text: string }
  | 'message.complete'      // Response finished: { message_id, ... }
  | 'thinking.delta'        // Thinking tokens (streaming): { text: string }
  | 'reasoning.delta'       // Reasoning tokens (streaming): { text: string }
  | 'reasoning.available'   // Reasoning text available (non-streaming)
  | 'status.update'         // Status change: { status: string, message?: string }
  | 'tool.start'            // Tool call started: { tool: string, input: any }
  | 'tool.progress'         // Tool progress update: { tool: string, ... }
  | 'tool.complete'         // Tool call finished: { tool: string, output: any, duration_ms: number }
  | 'tool.generating'       // Tool is generating (e.g. image gen): { tool: string, ... }
  | 'clarify.request'       // Agent needs clarification: { request_id, question, options? }
  | 'approval.request'      // Agent needs approval: { request_id, command, ... }
  | 'sudo.request'          // Agent needs sudo password: { request_id, ... }
  | 'secret.request'        // Agent needs secret: { request_id, prompt, ... }
  | 'background.complete'   // Background task finished
  | 'error'                 // Error: { message, code? }
  | 'skin.changed'          // Theme changed
  | 'review.summary'        // Self-improvement review summary
```

### Streaming Coalescing

`message.delta`, `reasoning.delta`, and `thinking.delta` are coalesced server-side into ~30fps batches (every 33ms) to reduce WebSocket frame churn. Non-streaming events (tools, approvals, status, completion) flush the buffer immediately.

## Client Library

Hermes Desktop ships `JsonRpcGatewayClient` in `apps/shared/src/json-rpc-gateway.ts`:

```typescript
import { JsonRpcGatewayClient, GatewayEvent } from '...'

const client = new JsonRpcGatewayClient({
  requestTimeoutMs: 30_000,
  connectTimeoutMs: 15_000,
})

await client.connect('ws://127.0.0.1:9119/api/ws')

// Subscribe to events
client.on('message.delta', (event: GatewayEvent<{ text: string }>) => {
  console.log('token:', event.payload?.text)
})

client.on('message.complete', () => {
  console.log('message done')
})

// Make RPC calls
const session = await client.request<{ session_id: string }>('session.create', {
  cols: 96,
  source: 'ai-os',
})

// Submit prompt (fire-and-forget, response via events)
await client.request('prompt.submit', {
  session_id: session.session_id,
  text: 'Hello!',
})

// Interrupt
await client.request('session.interrupt', { session_id: session.session_id })
```

## Integration Pattern

```
┌──────────────────────┐     WebSocket      ┌──────────────────────┐
│  Custom App (Tauri)  │  ────────────────  │  Hermes serve        │
│  JsonRpcGatewayClient │  jsonrpc 2.0      │  (port 9119)         │
│                      │  ◄────────────────  │                      │
│  Render events       │  streaming events  │  Agent loop          │
│  as chat UI          │                     │  + tool execution    │
└──────────────────────┘                     └──────────────────────┘
```

- The server is stateless from the client's perspective — sessions are tracked server-side.
- Multiple clients can connect to the same server simultaneously.
- Each session is independent; use `session.create` per project/conversation.
- `prompt.submit` returns immediately — all response data comes through events.
- Use `session.interrupt` for cancellation, not abort signals.