---
title: "Fix Music Candidate Search"
date: "2026-08-13"
conversation_id: "42f87d1d-7d45-4d3f-8bf1-9aec4601f50d"
source: "antigravity"
---

# Fix Music Candidate Search

## User

Fix candidate search issues in music-cross-linker:

1. Update `app/components/track-view/CandidateList.tsx`:
- Fix `runSearch` signature so `runSearch(e, currentLimit)` defaults `currentLimit` to `limit` state instead of defaulting to `10`.
- In `runSearch`, if `currentLimit` is provided, pass that `currentLimit` to the fetch URL query parameter `limit`.
- In `runSearch`, update `limit` state to `currentLimit` if it differs.
- In `loadMore`, update limit and pass `newLimit` directly into `runSearch`.

2. Update `app/api/entities/[id]/search/route.ts`:
- Add support for `platform === 'youtube'`.
- Import `searchYouTubeVideos` from `@/app/lib/youtube`.
- When `platform === 'youtube'`, call `await searchYouTubeVideos(query, limit)`.
- Map results to match candidates format:
  candidate_url: `https://www.youtube.com/watch?v=${v.id}`
  title: `v.title`
  artist: `v.channel`
  thumbnail_url: `v.thumbnail`
  rank: `i + 1`
  source: `'manual_search'`
  entity_id: `entityId`
  platform: `'youtube'`
- Insert non-empty youtube candidate rows into `match_candidates` with `sql\`INSERT INTO match_candidates ${sql(rows)} RETURNING *\`` and push to `candidates`.

Read files first if needed and apply changes carefully.

---

## Assistant

The requested updates for candidate search functionality have been implemented.

### Summary of Changes

1.  **[`CandidateList.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/track-view/CandidateList.tsx)**:
    *   Updated `runSearch` signature to default `currentLimit` to the current `limit` state instead of a hardcoded `10`.
    *   Updated `runSearch` to ensure the `limit` query parameter is passed correctly and that the `limit` state is updated to the `currentLimit` if it changes after a search.
    *   Adjusted `loadMore` to correctly update the limit state and trigger `runSearch` with the new limit.

2.  **[`route.ts`](file:///Users/matt/projects/music-cross-linker/app/api/entities/%5Bid%5D/search/route.ts)**:
    *   Added support for the `'youtube'` platform by importing `searchYouTubeVideos`.
    *   Implemented logic to call `searchYouTubeVideos(query, limit)` when the platform is `'youtube'`.
    *   Added logic to map YouTube search results to the required candidate format and insert them into the `match_candidates` database table.

---
