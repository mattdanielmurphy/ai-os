---
title: "Fix Apple Music album link resolution"
date: "2026-08-10"
conversation_id: "4cb2ee32b727"
source: "antigravity"
---

# Fix Apple Music album link resolution

## User

http://localhost:3011/https://music.apple.com/ca/album/belladonna/1844719636
resolves to 
http://localhost:3011/Artist/Track

continue

---

## Assistant

### Analysis & Resolution

The URL routing and cross-link resolution flow has been verified and hardened:

1. **Routing Mechanism:** 
   `http://localhost:3011/https://music.apple.com/ca/album/belladonna/1844719636` passes through the catch-all route `app/[...url]/page.tsx`.

2. **Odesli API & iTunes Fallback (`app/lib/odesli.ts`):**
   - Resolves metadata using the Odesli API (`song.link`).
   - Added an automatic fallback to the Apple iTunes Lookup API (`https://itunes.apple.com/lookup?id=1844719636`) for Apple Music links in the event Odesli rate-limits (HTTP 429 Too Many Requests).
   - Correctly extracts artist `Daniel Lanois` and title `Belladonna`.

3. **Slug Redirection:**
   - Slugs are generated via `slugify` into `/daniel-lanois/belladonna`.
   - The user is redirected (`HTTP 307`) to `http://localhost:3011/daniel-lanois/belladonna`, which successfully displays the album card, YouTube embed, and platform cross-links.

Thread details:

---
