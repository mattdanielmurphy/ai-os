---
name: music-cross-linker
description: No Spotify Web API. Uses SpotAPI on VPS for music lookups.
version: 1.0.0
author: Matt
license: MIT
---

# Music Cross-Linker Project Rules

## When to Use

Load this skill when working on the music-cross-linker Next.js project — resolving music URLs to cross-platform links, using the SpotAPI microservice on an Oracle Cloud VPS.

## ⚠️ CRITICAL: No Spotify Web API

**DO NOT suggest using the Spotify Web API (developer.spotify.com).**
The `/v1/search` endpoint and related Web API endpoints require a Spotify Premium account. This is NOT a free-tier API. Do NOT suggest creating a Spotify Developer app and getting client credentials — the user has investigated and confirmed this is blocked for non-Premium accounts.

The project uses **SpotAPI** (a Python library that scrapes Spotify's private GraphQL endpoints) running on an Oracle Cloud VPS.

## Architecture

- **SpotAPI microservice**: Python FastAPI service at `~/projects/spotapi-service/`, deployed on VPS `oracle-minecraft-server`
- **Next.js app**: Calls SpotAPI via HTTP to resolve Spotify URLs
- **Apple Music**: iTunes API search (free, no auth)
- **YouTube**: DuckDuckGo scraping

## Network

- VPS hostname: `oracle-minecraft-server` (SSH alias)
- SpotAPI public URL: `https://oracle-vps.tail491454.ts.net/` (Tailscale Funnel)
- Port: `8000`
- The VPS is on Oracle Cloud (data center IP) — Spotify blocks data center IPs

## Common Issues

- **Tailscale Funnel SSL**: Let's Encrypt cert via DNS-01 can fail. Check `journalctl -u tailscaled --no-pager -n 20` for ACME errors. Alternative: `cloudflared tunnel --url http://127.0.0.1:8000`
- **Data center IP block**: VPS Oracle Cloud IP blocked by Spotify. Workaround needed (residential proxy, Tailscale exit node)

## Resolution Flow

`urlResolver.ts` → `getPlatformLinks(artist, title, country, sourceUrl)`
- Apple Music: iTunes API
- Spotify: `FASTAPI_URL/search?q=...&is_album=...`
- YouTube: DuckDuckGo `!ducky`
- `FASTAPI_URL` env var (defaults to `http://localhost:8000`)