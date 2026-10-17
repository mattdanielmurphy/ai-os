---
name: hermes-gateway-api
description: "Configure and troubleshoot the Hermes Gateway HTTP API server — enabling port 8642, setting API_SERVER_KEY, and connecting external tools (Studio, dashboards, scripts) via bearer auth."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, gateway, api-server, configuration, troubleshooting, studio]
    related_skills: [hermes-agent]
---

# Hermes Gateway API Server

The Hermes Gateway can serve an **HTTP API server** on port 8642, which external tools (Hermes Studio, custom dashboards, CLI scripts, the ACP server) connect to for session management, chat, memory, skills, and config.

This API server is **opt-in** — it does not start by default, even when the gateway is running. It requires explicit configuration.

## Prerequisites

- Hermes Agent v0.18.0+ (the `API_SERVER_KEY` security check was added in v0.18.x)
- `hermes gateway run` already works (the gateway process starts for messaging platforms)

## Enabling the API Server

### 1. Enable the API server

Add to `~/.hermes/.env`:

```ini
API_SERVER_ENABLED=true
```

### 2. Set a secure API key

**Required.** The gateway v0.18.x refuses to start the API server without a key, even for loopback-only binds on `127.0.0.1`. The key must be:

- **At least 16 characters** — shorter keys are rejected with: `API_SERVER_KEY is a placeholder or too short (<16 chars)`
- **Not a placeholder** — `dev-key`, `test`, `secret`, etc. are rejected
- **Cryptographically random** — use `openssl rand -hex 16` or similar

```bash
# Generate a secure key
openssl rand -hex 16

# Add to ~/.hermes/.env
API_SERVER_KEY=28582603a4559f46346896b9741de429
```

### 3. Match the key in your client

Any tool connecting to the API server must send `Authorization: Bearer <API_SERVER_KEY>` as an HTTP header.

For **Hermes Studio**, add to the Studio's `.env`:

```ini
HERMES_API_TOKEN=28582603a4559f46346896b9741de429
```

### 4. Restart the gateway

```bash
hermes gateway run --replace
```

## Verification

Check the gateway is listening and the API server is healthy:

```bash
# Port should be listening
lsof -i :8642

# Health endpoint
curl http://localhost:8642/health

# Should return: {"status": "ok", "platform": "hermes-agent", "version": "0.18.2"}
```

## Common Errors

### `ECONNREFUSED 127.0.0.1:8642`

The gateway is running but the API server is not enabled. Check:

1. `API_SERVER_ENABLED=true` is set in `~/.hermes/.env`
2. `API_SERVER_KEY=<32-char-hex>` is set (≥16 chars, not a placeholder)
3. Gateway was restarted after adding these variables

### `API_SERVER_KEY is required for the API server`

The API server is enabled but no key was provided. Generate a key and add it to `.env`.

### `API_SERVER_KEY is a placeholder or too short (<16 chars)`

The key exists but is too short or guessable. Generate a proper key with `openssl rand -hex 16`.

### `Gateway connection refused / 401 Unauthorized`
The client's bearer token doesn't match the server's `API_SERVER_KEY`. Verify:

```bash
# Check the server's expected key
grep API_SERVER_KEY ~/.hermes/.env

# Check the client's token
grep HERMES_API_TOKEN /path/to/client/.env
```

### `Cannot read properties of undefined (reading 'slice')` (500 on `/api/history`)

The Studio connected but the API response format doesn't match. Hermes Gateway v0.18.x returns OpenAI-compatible list format (`{ object, data, limit, offset, has_more }`), but Studio expects `{ items, total }`.

**Fix:** Patch `listSessions()` and `getMessages()` in `src/server/hermes-api.ts` to handle both:

```typescript
return resp.data ?? resp.items ?? []
```

See `references/studio-gateway-connection.md` for full steps.

### `API server rejected invalid API key` (from Studio, using correct .env)

The Studio's `.env` has the right token, but there are two separate places in `vite.config.ts` where the token is needed:

**1. Vite SSR env gap** — `loadEnv` does NOT set `process.env` by default. The Studio's SSR code (in `src/server/gateway-capabilities.ts`) reads `process.env.HERMES_API_TOKEN` at import time — if it's not in the shell environment, the token is empty.

**Fix** — In `vite.config.ts`, forward loaded env vars to `process.env` right after `loadEnv`:

```typescript
const env = loadEnv(mode, process.cwd(), '')
// Forward env vars to process.env so SSR code can read them
for (const [k, v] of Object.entries(env)) {
  if (v && !(k in process.env)) process.env[k] = v
}
```

**2. Connection-status middleware probes** — the Vite middleware at `/api/connection-status` (in `configureServer`) makes direct `fetch` calls to the gateway to probe `/v1/models` and `/api/sessions`. These probes don't use the SSR auth headers — they need their own Bearer token.

**Fix** — Add auth headers to the fetch calls in the middleware:

```typescript
const authHeaders: Record<string, string> = env.HERMES_API_TOKEN
  ? { Authorization: `Bearer ${env.HERMES_API_TOKEN}` }
  : {}
// Pass to fetch calls:
fetch(`${hermesApiUrl}/v1/models`, { signal: ..., headers: authHeaders })
fetch(`${hermesApiUrl}/api/sessions?limit=1`, { signal: ..., headers: authHeaders })
```

Without both fixes, the Studio server-side code sends unauthenticated requests to the gateway, which logs repeated `API server rejected invalid API key` warnings from `user_agent='node'` even though the `.env` file is correct.

See `references/studio-gateway-connection.md` for the full guide.

## Configuration Reference

| Variable | Where | Purpose |
|----------|-------|---------|
| `API_SERVER_ENABLED=true` | `~/.hermes/.env` | Enables the HTTP API server on port 8642 |
| `API_SERVER_KEY=<hex>` | `~/.hermes/.env` | Shared secret used to validate bearer tokens |
| `HERMES_API_TOKEN=<hex>` | Client `.env` | Bearer token the client sends (must match `API_SERVER_KEY`) |
| `HERMES_API_URL=http://127.0.0.1:8642` | Client `.env` | URL of the gateway API server |

## Architecture

```
┌──────────────────────┐     Bearer: API_SERVER_KEY     ┌──────────────────────┐
│  Hermes Studio       │ ──────────────────────────────► │  Hermes Gateway      │
│  (Vite dev server)   │   GET /health                   │  (port 8642)         │
│                      │   GET /api/sessions             │                      │
│  HERMES_API_TOKEN ───┤   POST /api/sessions/...        │  API_SERVER_KEY ─────┤
│  HERMES_API_URL ─────┤   GET /api/skills               │  API_SERVER_ENABLED  │
└──────────────────────┘                                 └──────────────────────┘
```

## Related

- `references/websocket-jsonrpc-protocol.md` — the Hermes `serve`/`dashboard` WebSocket JSON-RPC protocol on port 9119 (separate from the API server above). Used by the Desktop app and custom integrations.

## Troubleshooting Flow

When a client can't reach the gateway API:

1. **Is the gateway running?** → `hermes gateway status`
2. **Is port 8642 open?** → `lsof -i :8642`
3. **Is the API server enabled?** → Check `grep API_SERVER_ENABLED ~/.hermes/.env`
4. **Is a key set?** → Check `grep API_SERVER_KEY ~/.hermes/.env`
5. **Does the client token match?** → Compare `API_SERVER_KEY` and `HERMES_API_TOKEN`
6. **Has the gateway been restarted since changes?** → `hermes gateway run --replace`
7. **Still failing?** → Check for stale process or Vite SSR env gap (see `references/studio-gateway-connection.md`)