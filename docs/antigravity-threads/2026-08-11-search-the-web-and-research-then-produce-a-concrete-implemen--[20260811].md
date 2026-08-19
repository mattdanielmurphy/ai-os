---
title: "Search the web and research, then produce a concrete implementation pl"
date: "2026-08-11"
conversation_id: "20260811_152302_48b345"
source: "antigravity"
---

# Search the web and research, then produce a concrete implementation pl

## User

Search the web and research, then produce a concrete implementation plan for the two problems below. Return the plan as a numbered markdown list with exact commands.

PROBLEM 1: Make a VPS at Oracle Cloud (Ubuntu, "oracle-minecraft-server", IP 40.233.124.200) with a FastAPI service on port 8000 accessible publicly WITHOUT an SSH tunnel. The VPS has Tailscale installed. Research how to use Tailscale Funnel to expose port 8000 publicly, including:
- Exact tailscale funnel command
- What domain the service gets
- Any gotchas (HTTPS certs, rate limits, etc.)
- Alternative: Cloudflare Tunnel (cloudflared) if Tailscale Funnel is insufficient

PROBLEM 2: The `spotapi` Python library (version 1.2.8) on the VPS internally crashes with `SongError: Could not get songs` when called from a data center IP. The library scrapes Spotify's internal GraphQL API. Research:
- Is there a newer/older version of spotapi that works?
- Are there alternatives to spotapi for scraping Spotify search results from a headless server?
- Can we use curl_cffi directly against Spotify's search endpoint to get track/album IDs?
- What about using the Spotify anonymous access token endpoint to get a valid token for search?
- Any known workarounds for the "Could not get songs" error from spotapi

Also include: exact changes needed in urlResolver.ts to switch from http://localhost:8000 to the public Tailscale Funnel URL, and how to handle the transition between local dev and production.

---

## Assistant

Here is the comprehensive research and step-by-step implementation plan for both problems.

---

### Implementation & Research Plan

#### Problem 1: Tailscale Funnel & VPS Setup for FastAPI

1. **Tailscale Funnel Configuration**
   - Tailscale Funnel securely routes public HTTPS traffic to local ports via Tailscale relays.
   - Run the following commands on the Oracle Cloud VPS (`oracle-minecraft-server`):
     ```bash
     # 1. Enable Funnel on your Tailscale tailnet ACLs if not already enabled via the Tailscale Admin Console.
     # 2. Configure serve mapping to your FastAPI local port 8000:
     tailscale serve --bg https / http://127.0.0.1:8000

     # 3. Enable Funnel for public HTTPS (port 443):
     tailscale funnel 443 on
     ```
   - **Assigned Domain:** Tailscale automatically provisions a domain in the format:
     `https://<node-name>.<tailnet-name>.ts.net` (e.g., `https://oracle-minecraft-server.tail1234.ts.net`).
   - **Gotchas:**
     - **TLS/HTTPS:** Tailscale automatically provisions and renews Let's Encrypt certificates for the `.ts.net` domain on port 443. No manual SSL setup is required.
     - **Rate Limits & Bandwidth:** Tailscale Funnel routes public traffic through Tailscale DERP relays, which may throttle high-bandwidth video/audio streaming or massive payload spikes. For API JSON payloads, it is fast and reliable.
     - **Allowed Ports:** Funnel natively supports ports `443`, `8443`, and `10000`. Public HTTP (port 80) automatically redirects to HTTPS (443).

2. **Cloudflare Tunnel (`cloudflared`) Alternative**
   - If Tailscale Funnel is insufficient (due to bandwidth limits, custom domain requirements, or latency):
     ```bash
     # Install cloudflared on Ubuntu
     sudo mkdir -p /etc/apt/keyrings
     curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /etc/apt/keyrings/cloudflare-main.gpg >/dev/null
     echo "deb [signed-by=/etc/apt/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared noble main" | sudo tee /etc/apt/sources.list.d/cloudflared.list
     sudo apt-get update && sudo apt-get install -y cloudflared

     # Run quick zero-config tunnel (returns a temporary https://*.trycloudflare.com URL)
     cloudflared tunnel --url http://127.0.0.1:8000
     ```

---

#### Problem 2: `spotapi` Datacenter IP Issue (`SongError: Could not get songs`)

1. **Root Cause Analysis**
   - `spotapi` (v1.2.8) scrapes Spotify's internal GraphQL web endpoints (`open.spotify.com/get_access_token` and client tokens).
   - Spotify actively blocks/challenges requests coming from known datacenter IP ranges (Oracle Cloud, AWS, GCP, Hetzner) and returns `400 Invalid TOTP` or `403 Forbidden` when generating anonymous web tokens without browser TLS fingerprinting/headers.

2. **Fixes & Workarounds**
   - **Option A: Official Spotify Client Credentials Flow via `curl_cffi` (Recommended & Stable)**
     - Spotify's official Web API allows server-to-server search (`/v1/search`) using the Client Credentials Flow without requiring user logins or datacenter IP restrictions.
     - Replace `spotapi` with standard `curl_cffi` or `httpx` targeting `https://accounts.spotify.com/api/token` with a free Spotify App Client ID + Client Secret.
   - **Option B: Use `curl_cffi` with Browser Impersonation for Spotify Web Access Token**
     - If you must avoid using official API credentials, generate an access token by mimicking Chrome browser headers and TLS signatures using `curl_cffi`:
       ```python
       from curl_cffi import requests

       # Get anonymous web client token/access token
       res = requests.get(
           "https://open.spotify.com/get_access_token",
           impersonate="chrome120",
           headers={"user-agent": "Mozilla/5.0 ..."}
       )
       token = res.json().get("accessToken")
       ```
   - **Option C: Proxy Datacenter Requests**
     - If keeping `spotapi`, route outgoing Spotify requests through residential proxies or a local home Tailscale exit node (bypassing Oracle Cloud's IP reputation).

---

#### Code Adjustments in `urlResolver.ts` & Dev/Prod Transition

1. **Environment Configuration in `urlResolver.ts`**
   - Use an environment variable (e.g. `SPOTIFY_API_URL` or `RESOLVER_SERVICE_URL`) with a fallback to `http://localhost:8000` for local development.

2. **Exact Changes Needed in `urlResolver.ts`**
   ```typescript
   // urlResolver.ts

   // Resolve base API URL dynamically from environment or default to local FastAPI dev server
   const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_FASTAPI_URL 
     || process.env.FASTAPI_URL 
     || 'http://localhost:8000';

   export async function resolveUrl(url: string) {
     const response = await fetch(`${FASTAPI_BASE_URL}/resolve`, {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ url }),
     });
     
     if (!response.ok) {
       throw new Error(`Failed to resolve URL: ${response.statusText}`);
     }

     return await response.json();
   }
   ```

3. **Handling Transition Between Local Dev and Production**
   - **Local Dev:** Put `FASTAPI_URL=http://localhost:8000` in `.env.local`.
   - **Production:** Set `FASTAPI_URL=https://oracle-minecraft-server.<your-tailnet>.ts.net` in deployment settings (Vercel, Docker, `.env.production`).

---
