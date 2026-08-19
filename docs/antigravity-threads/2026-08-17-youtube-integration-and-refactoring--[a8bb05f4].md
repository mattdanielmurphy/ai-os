---
title: "YouTube Integration And Refactoring"
date: "2026-08-17"
conversation_id: "a8bb05f4-fe00-4635-b8ac-d84a849e1c73"
source: "antigravity"
---

# YouTube Integration And Refactoring

## User

Please update the YouTube search and CandidateList integration across the following files:

1. `app/lib/youtube.ts`:
Update `searchYouTubeVideos(query: string, limit = 10)` to parse `ytInitialData` from the YouTube search results HTML.
- Extract `ytInitialData` using `html.match(/var ytInitialData = ({.*?});<\/script>/)`. If found, parse JSON and traverse `twoColumnSearchResultsRenderer.primaryContents.sectionListRenderer.contents` to extract each `itemSectionRenderer.contents[].videoRenderer` (`videoId`, `title` from runs/simpleText, `channel` from ownerText/shortBylineText runs, `thumbnail` from thumbnails[0].url).
- Provide a regex fallback matching `/"videoId"\s*:\s*"([a-zA-Z0-9_-]{11})"/g` if JSON parse fails.
- In `getTopVideos`, ensure query text handles album vs track appropriately (`artist + ' ' + title + ' full album'` for album, `artist + ' ' + title + ' official audio'` for track).

2. `app/lib/urlResolver.ts`:
In `resolveYoutubePlatform(ctx: EntityContext, sourceUrl?: string)`:
- Remove the unreliable DuckDuckGo `!ducky` scraping.
- Instead, call `getTopVideos(cleanArtist || cleanTitle, cleanTitle, isAlbum ? 'album' : 'track', 5)`.
- For each returned video, compute `classifyMatch(video.title, video.channel, cleanTitle, cleanArtist)`.
- Insert all returned candidates into `match_candidates` with rank (1 to N), source='youtube_search', and numeric confidence.
- Select the highest-confidence candidate (or top candidate) and call `saveAutoMatch(entityId, 'youtube', youtubeUrl, bestCandidateId)`.
- Return the resolved `{ url, matchedBy, candidates }`.

3. Create `app/components/track-view/YouTubePlayer.tsx`:
A client component ('use client') that wraps the iframe and CandidateList:
Props: {
  initialVideoId: string;
  artist: string;
  title: string;
  entityId: string;
  isExplicitSource: boolean;
  candidates: any[];
  currentUrl: string;
  searchTerm: string;
}
State:
- `currentVideoId` initialized to `initialVideoId`.
- `currentUrl` state initialized to props.currentUrl.
- `handleUpdateMatch`: updates `currentVideoId` (extracting the 11-char video ID from the newly selected URL) and `currentUrl`, so selecting a candidate in CandidateList immediately switches the playing video.

4. Update `app/components/track-view/YouTubeSection.tsx`:
- Render `<YouTubePlayer ... />` passing down the initial resolved video ID, candidate list, and metadata.

Ensure `bun run build` passes with zero errors.

---
