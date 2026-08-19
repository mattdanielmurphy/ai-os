---
title: "Fix two issues in music-cross-linker codebase:"
date: "2026-08-10"
conversation_id: "598702fc-aee1-483c-a7c1-e61c590e0d4d"
source: "antigravity"
---

# Fix two issues in music-cross-linker codebase:

## User

Fix two issues in music-cross-linker codebase:

1. In `app/[artist]/[track]/page.tsx`:
Remove the duplicate `{videoId && ...}` iframe block so there is strictly ONE YouTube player iframe.

2. In `app/[...url]/page.tsx`:
When `odesliData` is returned by `fetchOdesliByUrl(url)`, extract `odesliData.type` (if set) to determine `type = odesliData.type`.
Also, when fallback parsing Apple Music URLs, if `!trackIdMatch` and `albumIdMatch`, ensure `type = 'album'`!

3. In `app/lib/urlResolver.ts`:
Make sure `odesli.spotifyUrl`, `odesli.appleUrl`, and `odesli.youtubeUrl` obtained from `fetchOdesliByUrl(src)` are assigned to `appleUrl`, `spotifyUrl`, `youtubeUrl` whenever available (if `!appleUrl`, `!spotifyUrl`, `!youtubeUrl`).
Also, if `!spotifyUrl`, when attempting iTunes / DuckDuckGo search or fallback, if type === 'album', search Spotify for `site:open.spotify.com/album`.

Modify `app/[artist]/[track]/page.tsx`, `app/[...url]/page.tsx`, and `app/lib/urlResolver.ts` directly.

---
