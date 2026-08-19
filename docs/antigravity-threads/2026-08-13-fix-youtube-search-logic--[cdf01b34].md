---
title: "Fix YouTube Search Logic"
date: "2026-08-13"
conversation_id: "cdf01b34-fb5c-4592-a145-1414156561ae"
source: "antigravity"
---

# Fix YouTube Search Logic

## User

Fix YouTube search candidate issues in music-cross-linker:

1. Update `app/lib/youtube.ts`:
In `searchYouTubeVideos(query: string, limit = 10)`:
Change the regex matching logic for `videoRenderer` blocks. Currently `html.matchAll(/"videoRenderer":\s*({[\s\S]*?})(?=,\s*"videoRenderer"|\]\}\}\}\})/g)` stops early or matches truncated JSON blocks.
Update it to accurately match video renderers throughout the document or split/parse videoId blocks cleanly so it extracts all returned videos (up to `limit`).
For example:
```ts
const videoMatches = Array.from(
  html.matchAll(/"videoRenderer"\s*:\s*(\{[\s\S]*?\})(?=,\s*"videoRenderer"|,\s*"compactVideoRenderer"|,\s*"continuationItemRenderer"|\]\}\}\}\})/g)
);
```
Or parse using `"videoId":"..."` occurrences across `videoRenderer` blocks. Ensure that for a standard query, it returns up to 20-30 candidates cleanly without stopping at 3.

2. Update `app/api/entities/[id]/search/route.ts`:
Make sure `rank` is computed cleanly and inserted rows handle conflict or ON CONFLICT so `Load More` appends/updates properly instead of returning empty or duplicate sets.
Or if `sql\`INSERT INTO match_candidates ...\`` is used, add `ON CONFLICT (entity_id, platform, candidate_url) DO UPDATE SET rank = EXCLUDED.rank, title = EXCLUDED.title, artist = EXCLUDED.artist, thumbnail_url = EXCLUDED.thumbnail_url RETURNING *` or fetch the updated list from `match_candidates` for `(entity_id, platform)`.
Specifically, in `app/api/entities/[id]/search/route.ts`:
After inserting/upserting candidates into `match_candidates` for ANY platform (`spotify`, `youtube`, `apple_music`), query all match candidates for that `entity_id` and `platform` ordered by `rank ASC` or `created_at ASC` limit `limit`:
```ts
const allCandidates = await sql`
  SELECT * FROM match_candidates
  WHERE entity_id = ${entityId} AND platform = ${platform}
  ORDER BY rank ASC
  LIMIT ${limit}
`;
```
And return `candidates: allCandidates` in the JSON response!
This guarantees that as `limit` increases (10 -> 20 -> 30) when clicking "Load More", the endpoint returns the full accumulated list up to `limit`, rather than just the new insertion batch!

Apply these edits carefully to both `app/lib/youtube.ts` and `app/api/entities/[id]/search/route.ts`.

---

## Assistant

OK. I have completed the requested updates.

1.  **Updated `app/lib/youtube.ts`**: Modified the `searchYouTubeVideos` regex to accurately capture video renderer blocks by including additional potential renderer types in the lookahead assertion.
2.  **Updated `app/api/entities/[id]/search/route.ts`**: Replaced the direct `INSERT` with an `UPSERT` (`INSERT ... ON CONFLICT ... DO UPDATE`) for Spotify, YouTube, and Apple Music search candidates. After each insertion, the endpoint now fetches the accumulated set of candidates up to the requested `limit`, ensuring that "Load More" behavior correctly returns the full set of results.

Changes have been sent to the parent agent.

---
