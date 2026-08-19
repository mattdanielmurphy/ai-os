---
title: "Update YouTube Title Parsing"
date: "2026-08-13"
conversation_id: "dac4b48b-47cb-463b-a487-262762ca78cc"
source: "antigravity"
---

# Update YouTube Title Parsing

## User

Update `/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts` to import `cleanYouTubeTitle` and `parseYouTubeTitle` from `./youtube/titleParser`.

Use `parseYouTubeTitle` in `resolveEntity` when `sourcePlatform === 'youtube'` or when title parsing YouTube video titles, so that `cleanArtist` and `cleanTitle` are sanitized right from the start before querying Spotify (`spotapi-service`) or Apple Music.

Specific edit in `resolveEntity`:
If `sourcePlatform === 'youtube'` or title contains YouTube noise tags / delimiters:
Run `const parsed = parseYouTubeTitle(title || '', artist);`
If `parsed.artist` exists and `!artist` (or artist === 'Unknown Artist'), set `cleanArtist = parsed.artist`.
Set `cleanTitle = parsed.title || cleanTitle`.

Also in `resolveYoutubePlatform`:
When fetched `oembed.title` (or ducky title `yTitle`), run `cleanYouTubeTitle(yTitle)` on candidate titles stored or displayed.

Ensure no syntax errors or breaking changes.

---

## Assistant

The requested updates have been implemented in [`/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts).

### Summary of Changes

1.  **Imports**: Added `cleanYouTubeTitle` and `parseYouTubeTitle` from `./youtube/titleParser`.
2.  **`resolveEntity`**: Sanitization logic was added. If the `sourcePlatform` is `'youtube'` or if the title contains common YouTube noise delimiters (`(`, `[`, `{`), the `parseYouTubeTitle` utility is called. It correctly updates `cleanArtist` (if it was previously unknown) and `cleanTitle` based on the parsed results.
3.  **`resolveYoutubePlatform`**: Added `cleanYouTubeTitle` calls when processing YouTube `oembed` titles to ensure candidate titles are clean before storage or display.

---
