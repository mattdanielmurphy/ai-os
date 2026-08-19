---
title: "Fixing Music Metadata Scraper"
date: "2026-08-19"
conversation_id: "b4391822-940e-44a2-ab27-dc5cc7ef3ceb"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 19, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">when I type `http://localhost:3011/https://music.apple.com/ca/album/belladonna/1844719636`<br>I end up with the title: `Belladonna - Album by Daniel Lanois | Spotify`<br>Basically it's matching spotify and scraping the spotify site (presumably) but taking the whole title instead of actually properly getting the artist and title.<br>Fix that please.</span>



<span title="Responded at 8:07am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

### Summary of Fix

The issue was caused by Spotify metadata scraping saving raw OpenGraph/page `<title>` strings (such as `"Belladonna - Album by Daniel Lanois | Spotify"`) directly into the database's `match_candidates.title` column. When [`resolveEntity`](file:///Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts#L450-L460) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts%3A450%3A460) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts) hydrated the canonical title for the page header (`<h1>`) and metadata (`<title>`), it picked the uncleaned string rather than extracting the clean album title and artist.

---

### Key Changes Made

1. **Spotify Title Parser ([`app/lib/youtube/titleParser.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts))**:
   - Implemented [`parseSpotifyTitle`](file:///Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts#L65-L113) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts%3A65%3A113) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts) to parse Spotify album, single, EP, compilation, and track title strings (`"<Title> - (Album|Single|EP|Compilation) by <Artist> | Spotify"` and `"<Title> - song and lyrics by <Artist> | Spotify"`), extracting clean `title`, `artist`, and entity `type`.
   - Wired `parseSpotifyTitle` into [`cleanYouTubeTitle`](file:///Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts#L115-L125) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts%3A115%3A125) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts), [`parseYouTubeTitle`](file:///Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts#L127-L150) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts%3A127%3A150) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts), and [`parseMusicTitle`](file:///Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts#L255-L270) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts%3A255%3A270) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts) to strip platform noise across all render paths.

2. **Metadata Scraper & Entity Resolution ([`app/lib/urlResolver.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts))**:
   - Enhanced [`fetchSpotifyMetadata`](file:///Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts#L126-L177) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts%3A126%3A177) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts) to parse JSON-LD structured data (`MusicAlbum` / `MusicRecording` schema with exact `name` and `byArtist`) with automatic fallback to `parseSpotifyTitle`.
   - Updated User-Agent to `facebookexternalhit/1.1` to ensure Spotify servers always return full SSR OpenGraph and JSON-LD payloads.
   - Sanitized candidate `title` and `artist` before inserting into Postgres `match_candidates` in [`resolveSpotifyPlatform`](file:///Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts#L595-L665) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts%3A595%3A665) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts).
   - Sanitized `canonicalTitle` and `canonicalArtist` in [`resolveEntity`](file:///Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts#L450-L460) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts%3A450%3A460) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts).
   - Updated candidate query sorting to `ORDER BY confidence DESC NULLS LAST, rank ASC`.

3. **Odesli Direct Spotify Fallback ([`app/lib/odesli.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/odesli.ts#L48-L66) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/odesli.ts%3A48%3A66) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/odesli.ts))**:
   - Added direct Spotify metadata extraction in [`fetchOdesliByUrl`](file:///Users/matt/projects/music-cross-linker/app/lib/odesli.ts) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/odesli.ts) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/odesli.ts) so pasted Spotify links resolve instantly to canonical slugs.

4. **UI Components ([`PlatformButton.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/track-view/PlatformButton.tsx) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/components/track-view/PlatformButton.tsx) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/components/track-view/PlatformButton.tsx), [`MatchCard.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/track-view/MatchCard.tsx) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/components/track-view/MatchCard.tsx) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/components/track-view/MatchCard.tsx))**:
   - Replaced ad-hoc `.split(' - Album by ')` slices with `cleanYouTubeTitle` for uniform candidate and button labels.

5. **Database Cleanup & Unit Tests ([`titleParser.test.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.test.ts) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.test.ts) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.test.ts))**:
   - Cleaned all contaminated rows in the `match_candidates` database table.
   - Added unit tests for Spotify title parsing and cleaning (all 23 tests passing).

---

### Verification

Navigating to `http://localhost:3011/https://music.apple.com/ca/album/belladonna/1844719636`:
- **Slug**: `/daniel-lanois/belladonna`
- **Page Title**: `Daniel Lanois - Belladonna | Multilink`
- **Header (`<h1>`)**: `Belladonna`
- **Artist (`<h2>`)**: `Daniel Lanois`

---
*Thread Context: [thread.md](file:///Users/matt/.gemini/antigravity/brain/b4391822-940e-44a2-ab27-dc5cc7ef3ceb/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/b4391822-940e-44a2-ab27-dc5cc7ef3ceb/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/b4391822-940e-44a2-ab27-dc5cc7ef3ceb/thread.md) | Backlog: [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)*

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | Committed | PPLX Quota | Handoff |
| :--- | :--- | :--- | :--- | :--- |
| ~130k / ~450k 🟡 (fatigue) | 3:05am | 🟢 Clean | 89 ❓, 37 📤 | [⚡ -60% context · -10% cost T1](http://127.0.0.1:3031/handoff?session=b4391822-940e-44a2-ab27-dc5cc7ef3ceb) |

<span style="position: absolute; right: 2rem; bottom: 0.5rem; display: inline-block; font-size: 11px; font-weight: 600; opacity: 0.7; padding: 3px 10px; border: 1px solid rgba(113,100,175,0.4); border-radius: 20px; white-space: nowrap; letter-spacing: 0.3px;"><a href="file:///Users/matt/.gemini/antigravity/brain/b4391822-940e-44a2-ab27-dc5cc7ef3ceb/kanban.md" style="text-decoration:none;">📋 Kanban</a></span>

</span>

</span>