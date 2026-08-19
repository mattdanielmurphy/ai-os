---
title: "Please update /Users/matt/projects/music-cross-linker/app/lib/odesli.t"
date: "2026-08-10"
conversation_id: "022a4199-871e-4679-95eb-77b781ef1246"
source: "antigravity"
---

# Please update /Users/matt/projects/music-cross-linker/app/lib/odesli.t

## User

Please update /Users/matt/projects/music-cross-linker/app/lib/odesli.ts to fallback to parsing Apple Music URL path metadata (extracting title and artist/id) or using iTunes API directly when api.song.link returns non-200 (e.g. 429 Too Many Requests).

Specifically:
1. In `fetchOdesliByUrl(sourceUrl: string)`, if `!res.ok`, check if `sourceUrl` is an Apple Music URL (e.g., matching `music.apple.com/ca/album/belladonna/1844719636` or `music.apple.com/ca/album/album-name/id1844719636` or `music.apple.com/ca/artist/artist-name/id...`).
2. Parse the URL slug (e.g. `/album/belladonna/1844719636` or `/album/belladonna/id1844719636`) or query iTunes lookup API `https://itunes.apple.com/lookup?id=1844719636`.
iTunes lookup API return object:
`const lookup = await fetch('https://itunes.apple.com/lookup?id=' + id).then(r => r.json()).catch(() => null);`
`const item = lookup?.results?.[0];`
If `item` exists:
- `title`: `item.collectionName || item.trackName`
- `artistName`: `item.artistName`
- `type`: `item.wrapperType === 'collection' ? 'album' : 'track'`
- `appleUrl`: `item.collectionViewUrl || item.trackViewUrl`
Return these parsed values so `fetchOdesliByUrl` returns `{ title, artistName, type, appleUrl, originalUrl: sourceUrl }`.
If iTunes lookup also fails or URL doesn't have ID, fallback to slug title extraction from URL path if possible.

---
