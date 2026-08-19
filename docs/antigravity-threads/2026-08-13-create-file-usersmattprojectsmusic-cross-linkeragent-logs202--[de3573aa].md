---
title: "Create file /Users/matt/projects/music-cross-linker/agent-logs/2026-08-12_18-21_fix-vps-tailscale-funnel-502.md with the following content:"
date: "2026-08-13"
conversation_id: "de3573aa-9968-433f-bbd4-f5929560f9de"
source: "antigravity"
---

# Create file /Users/matt/projects/music-cross-linker/agent-logs/2026-08-12_18-21_fix-vps-tailscale-funnel-502.md with the following content:

## User

Create file /Users/matt/projects/music-cross-linker/agent-logs/2026-08-12_18-21_fix-vps-tailscale-funnel-502.md with the following content:

# VPS Tailscale Funnel Port & SpotAPI 502 Resolution

## Root Cause
1. **Tailscale Funnel Port Mismatch**: Tailscale Funnel on `oracle-vps.tail491454.ts.net` was proxying public traffic to port `4242` instead of port `8000` (where PM2 `spotapi-service` runs). This caused all incoming requests to return HTTP 502 Bad Gateway.
2. **Duplicate Error Logging**: When `callSpotapiEntity` failed on the primary endpoint (`search-album`), `searchSpotifyViaSpotapi` attempted the fallback endpoint (`search-track`), producing a second 502 error.

## Fix Applied
1. **VPS Configuration**: Updated Tailscale Funnel on the VPS via `tailscale funnel --bg 8000` to proxy directly to `127.0.0.1:8000`. Verified health check (`/api/spotify/health`) and live search lookups via `curl`.
2. **Short-Circuit Error Logic**: Updated `callSpotapiEntity` and `searchSpotifyViaSpotapi` in `app/lib/urlResolver.ts` to flag HTTP 5xx server errors and return `null` immediately, preventing unnecessary fallback retries and duplicate 502 logs when the service is unreachable.

---

Append the following bullet to /Users/matt/projects/music-cross-linker/DEVELOPMENT_JOURNAL.md:
- August 12, 2026 - Fixed SpotAPI 502 Bad Gateway by re-pointing VPS Tailscale Funnel to port 8000. Short-circuited SpotAPI fallback lookups on server errors in `urlResolver.ts`.

---
