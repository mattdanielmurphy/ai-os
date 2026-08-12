# Hermes Studio ↔ Gateway Connection Debugging

## Symptom

Studio dev server starts at `http://localhost:3000/` but the gateway shows:
```
WARNING gateway.platforms.api_server: API server rejected invalid API key:
  remote='127.0.0.1' path='/api/sessions' user_agent='node'
```
And the UI shows "disconnected" or can't load sessions/skills/config.

## Root Cause Chain

1. **Old process stale token** — if the Studio dev server was started *before* `HERMES_API_TOKEN` was added to `.env`, the running Node process has an empty token. Must kill the old process (`pkill -f "vite dev"` or `kill <PID>`) before restarting.

2. **Vite SSR env gap** — even with the correct `.env`, Vite's `loadEnv(mode, process.cwd(), '')` loads env vars into a config-scoped object. It does NOT set them on `process.env`. Studio SSR code (`src/server/gateway-capabilities.ts`, `src/server/hermes-api.ts`) reads `process.env.HERMES_API_TOKEN` directly — so it sees an empty string.

   **Fix:** Patch `vite.config.ts` to forward loaded env vars:
   ```typescript
   const env = loadEnv(mode, process.cwd(), '')
   for (const [k, v] of Object.entries(env)) {
     if (v && !(k in process.env)) process.env[k] = v
   }
   ```

3. **Connection-status middleware probe auth** — the Vite middleware at `/api/connection-status` makes its own `fetch` calls to the gateway to detect the connection mode. Even after fixing the SSR env gap, these middleware probes still go out without the Bearer token, generating "rejected invalid API key" warnings in the gateway log.

   **Fix:** Add `authHeaders` to the fetch calls in the middleware at `configureServer` in `vite.config.ts`:
   ```typescript
   const authHeaders: Record<string, string> = env.HERMES_API_TOKEN
     ? { Authorization: `Bearer ${env.HERMES_API_TOKEN}` }
     : {}
   // then pass headers: authHeaders to the fetch calls
   fetch(`${hermesApiUrl}/v1/models`, { headers: authHeaders, ... })
   fetch(`${hermesApiUrl}/api/sessions?limit=1`, { headers: authHeaders, ... })
   ```

4. **Gateway auth mismatch** — the gateway's `API_SERVER_KEY` and the Studio's `HERMES_API_TOKEN` must match exactly. The key must be ≥16 characters and not a placeholder.

## Verification

```bash
# 1. Studio .env has the token
grep HERMES_API_TOKEN /path/to/Hermes-Studio/.env

# 2. Gateway .env has matching key
grep API_SERVER_KEY ~/.hermes/.env

# 3. Gateway is listening on 8642
curl http://localhost:8642/health

# 4. Auth works (use the actual token)
curl -H "Authorization: Bearer $(grep HERMES_API_TOKEN /path/to/Studio/.env | tail -1 | cut -d= -f2)" \
  http://localhost:8642/api/sessions?limit=1

# 5. Studio proxy works (from browser or curl)
curl http://localhost:3000/api/hermes-config

# 6. Gateway log is clean of auth rejections
tail -5 ~/.hermes/logs/gateway.log
# Should show no "rejected invalid API key" lines
```

## Caveat: Patches Against Upstream

The `vite.config.ts` env-forward loop, the middleware auth headers, and the `hermes-api.ts` `data`→`items` fallback are **local patches** to an external repo (Hermes Studio). A `git pull` on the Studio repo may overwrite them. After pulling, re-check:

- `vite.config.ts` — the `for (const [k, v] of Object.entries(env))` loop right after `loadEnv`
- `vite.config.ts` — the `authHeaders` in the `/api/connection-status` middleware in `configureServer`
- `src/server/hermes-api.ts` — the `resp.data ?? resp.items ?? []` fallback in `listSessions()` and `getMessages()`

If gone, re-apply from the fixes above.

## Logs

| Source | Location |
|--------|----------|
| Gateway API auth failures | `~/.hermes/logs/gateway.log` |
| Vite dev server | Terminal stdout (`pnpm dev`) |
| SSR module initialization | Browser console / Vite terminal |

## API Response Format Mismatch (v0.18.x Gateway)

**Symptom:** Studio loads but returns 500 on `/api/history?sessionKey=...` with error:
```
Cannot read properties of undefined (reading 'slice')
```
Or Studio says "disconnected" despite gateway auth working.

**Cause:** Hermes Gateway v0.18.x returns OpenAI-compatible list format for sessions and messages:
```json
{ "object": "list", "data": [...], "limit": 50, "offset": 0, "has_more": false }
```
But Studio's `src/server/hermes-api.ts` expects:
```typescript
{ items: Array<HermesSession>, total: number }
```
The `items` field is `undefined` → `resp.items` returns `undefined` → `.slice()` throws.

**Fix:** In `src/server/hermes-api.ts`, patch `listSessions()` and `getMessages()` to read `data` first with fallback:
```typescript
return resp.data ?? resp.items ?? []
```

**Verification:** After fixing, curl the Studio's history endpoint directly:
```bash
curl http://localhost:3000/api/history?limit=5&sessionKey=main
# Should return JSON with messages array, not a 500
```

**Positive signal:** The dev server log shows:
```
[gateway] http://127.0.0.1:8642 mode=enhanced-hermes
  core=[health, chatCompletions, models, streaming]
  enhanced=[sessions, enhancedChat, jobs]
```
The `mode=enhanced-hermes` confirms both auth AND API format are working.

## Order of Operations (recovery)

1. Kill all Studio dev server processes: `pkill -f "vite dev"`
2. Ensure gateway `.env` has `API_SERVER_ENABLED=true` and `API_SERVER_KEY=<32-char-hex>`
3. Ensure Studio `.env` has `HERMES_API_TOKEN=<same-hex>`
4. Patch `vite.config.ts` with the `process.env` forward loop if not present
5. Patch `vite.config.ts` with auth headers on the connection-status middleware probes
6. Patch `src/server/hermes-api.ts` with `data` → `items` fallback if Studio 500s
7. Restart gateway: `hermes gateway run --replace`
8. Wait 3s, verify: `curl localhost:8642/health`
9. Start Studio: `pnpm dev`
10. Verify: `curl localhost:<port>/api/hermes-config`
11. Verify: `curl 'localhost:<port>/api/history?limit=1&sessionKey=main'`
12. Verify: `tail -3 ~/.hermes/logs/gateway.log` — no "rejected" lines
