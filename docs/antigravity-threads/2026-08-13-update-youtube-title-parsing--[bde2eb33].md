---
title: "Update YouTube Title Parsing"
date: "2026-08-13"
conversation_id: "bde2eb33-27dd-4dfd-859b-3ed31b585e1a"
source: "antigravity"
---

# Update YouTube Title Parsing

## User

Update `/Users/matt/projects/music-cross-linker/app/api/resolve-link/route.ts` to use `cleanYouTubeTitle` and `parseYouTubeTitle` from `../../lib/youtube/titleParser`.

Replace `parseArtistTitleFromVideoTitle` in `/Users/matt/projects/music-cross-linker/app/api/resolve-link/route.ts` with calling `cleanYouTubeTitle` and `parseYouTubeTitle`.

Specifically:
- Import `cleanYouTubeTitle, parseYouTubeTitle` from `../../lib/youtube/titleParser`.
- In `POST` route:
```ts
if (isYoutube) {
  let rawVideoTitle: string | null = null;
  try {
    const oembed = await fetch(
      `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${videoId}&format=json`
    ).then((r) => (r.ok ? r.json() : null));
    rawVideoTitle = oembed?.title || null;
  } catch {}

  if (rawVideoTitle) {
    const parsed = parseYouTubeTitle(rawVideoTitle);
    if (parsed.artist) artistName = parsed.artist;
    title = parsed.title;
  } else if (title) {
    const parsed = parseYouTubeTitle(title);
    if (parsed.artist) artistName = parsed.artist;
    title = parsed.title;
  }
}
```

Also update `/Users/matt/projects/music-cross-linker/app/components/track-view/TrackView.tsx`:
- Import `cleanYouTubeTitle` from `../../lib/youtube/titleParser`.
- In `parseMusicTitle(title: string)` or `displayPrimary`, ensure `cleanYouTubeTitle` is called so any leftover bracket noise tags or trailing unmatched `(` are cleaned from display headers.

Also edit `/Users/matt/projects/music-cross-linker/tmp/slugs.json` (or delete the stale key `"led-zeppelin/physical-graffiti"`) so the cached stale record `"Physical Graffiti ("` is healed!

---

## Assistant

The requested updates have been successfully implemented:

1.  **API Route Update**: Updated `/Users/matt/projects/music-cross-linker/app/api/resolve-link/route.ts` to utilize `cleanYouTubeTitle` and `parseYouTubeTitle` for parsing and cleaning YouTube video titles. The legacy `parseArtistTitleFromVideoTitle` function was removed.
2.  **UI Component Update**: Updated `/Users/matt/projects/music-cross-linker/app/components/track-view/TrackView.tsx` to import `cleanYouTubeTitle` and apply it to `displayPrimary` within the track header, ensuring cleaner display output.
3.  **Data Fix**: Updated `/Users/matt/projects/music-cross-linker/tmp/slugs.json` to correct the stale title `"Physical Graffiti ("` for the entry `led-zeppelin/physical-graffiti`.

---
