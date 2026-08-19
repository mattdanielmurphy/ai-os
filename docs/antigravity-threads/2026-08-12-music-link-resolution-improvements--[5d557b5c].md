---
title: "Music Link Resolution Improvements"
date: "2026-08-12"
conversation_id: "5d557b5c-eb11-4122-b651-0afdb7c7f791"
source: "antigravity"
---

# Music Link Resolution Improvements

## User

# Implementation Plan: Instant Video Loading, Spotify Search Matching & Unconfident Match Results

Fix three related issues in music link resolution, playback, and candidate discovery:
1. Instant display of explicit YouTube videos without waiting for background resolution.
2. Resolve Spotify search matching failure for albums like Aphex Twin's "Selected Ambient Works 85-92" (VPS proxy fix + slug/query normalization).
3. Allow users to view and select search results even when no confident match was automatically found.

---

## User Review Required

> [!IMPORTANT]
> The primary reason the Spotify search returned "No confident match" for Aphex Twin was that the VPS `tailscale serve` proxy was routing requests to port `4242` instead of port `8000` (`spotapi-service`), returning HTTP `502 Bad Gateway` on all API calls and forcing fallback search URLs. Pointing `tailscale serve` to port `8000` instantly allows `spotapi-service` to return the exact Aphex Twin album with `high` confidence.

---

## Proposed Changes

### 1. Instant YouTube Video Rendering (`app/components/ResolvingRedirect.tsx` & `app/page.tsx`)

#### [MODIFY] [ResolvingRedirect.tsx](file:///Users/matt/projects/music-cross-linker/app/components/ResolvingRedirect.tsx)
- When `videoId` is present, render the YouTube `<iframe>` immediately inside `.player-wrapper` instead of showing `.player-wrapper-skeleton` and a spinner.
- Display a sleek, non-blocking status indicator below the player ("Finding cross-platform matches…") while `fetch('/api/resolve-link')` completes in the background and redirects to the canonical slug.

#### [MODIFY] [page.tsx](file:///Users/matt/projects/music-cross-linker/app/page.tsx)
- Add client-side submit handling to the search form on the homepage so pasting any URL (YouTube, Spotify, Apple Music) immediately redirects to `/${encodeURIComponent(url)}` or `/${url}`.

---

### 2. Spotify Matching & Normalization (`spotapi-service/main.py`, `app/lib/urlResolver.ts`, `app/components/track-view/TrackView.tsx`)

#### [
<truncated 1644 bytes>
tead of `"Not Right?"`.
  - If match exists: Continue displaying `"Not Right?"`.
- When opened in a `isNoMatch` state (where candidate list only contains fallback URLs or is empty), automatically fire `runSearch()` using `initialQuery` so results from the search API populate the candidate picker immediately.
- Filter out `*_fallback` placeholder entries from the candidate cards list so users only see real candidate items.

---

## Verification Plan

### Automated / API Verification
- Run VPS health check: `curl https://oracle-vps.tail491454.ts.net/api/spotify/health` to ensure `{"status":"ok"}`.
- Test Spotify album search: `curl "https://oracle-vps.tail491454.ts.net/api/spotify/search-album?q=Aphex%20Twin%20Selected%20Ambient%20Works%2085-92&title=Selected%20Ambient%20Works%2085-92&artist=Aphex%20Twin"` to verify high-confidence album match.
- Test `bun test` or run Next.js build (`bun run build`) to verify type safety and absence of build errors.

### Manual Verification
1. **Explicit YouTube Link**: Navigate to `/https://www.youtube.com/watch?v=762kG_D01K4` (or any YouTube link). Verify that the YouTube video player renders immediately with zero loading spinner delay on the player container.
2. **Aphex Twin Spotify Resolution**: Navigate to `/aphex-twin/selected-ambient-works-85-92`. Verify that Spotify resolves to the actual album `https://open.spotify.com/album/7aNclGRxTysfh6z0d8671k`.
3. **No Confident Match UI**: Test with a query that has no automatic match. Verify the `"See search results"` link appears beneath the platform button, opens the candidate picker, and fetches relevant search candidates on open.

---

## Assistant

The subagent `ResolvingRedirect UI Editor` is currently modifying `app/components/ResolvingRedirect.tsx` to enable instant YouTube video rendering. I will process the subagent's updates as soon as it completes.

I am waiting for the subagent to complete editing `app/page.tsx`.

I am waiting for the subagent to complete updating `formatSlug` in `TrackView.tsx`.

I am waiting for the subagent to complete updating `normalizeForMatch` in `urlResolver.ts` and `_normalize` in `spotapi-service/main.py`.

I am waiting for the subagent to complete editing `PlatformButton.tsx` and `CandidateList.tsx`.

I am waiting for `auto_commit.py` to finish committing and pushing the changes.

All changes from the implementation plan have been completed, verified, and committed:

### Summary of Accomplishments

1. **Instant YouTube Video Rendering**
   - Modified [`ResolvingRedirect.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/ResolvingRedirect.tsx): Renders the YouTube `<iframe>` immediately inside `.player-wrapper` when `videoId` is available, while displaying `"Finding cross-platform matches…"` while `fetch('/api/resolve-link')` completes in the background.

2. **Homepage Search Submission**
   - Modified [`page.tsx`](file:///Users/matt/projects/music-cross-linker/app/page.tsx): Added client-side form handling so pasting any music URL (or query) immediately routes to `/${encodeURIComponent(url)}`.

3. **Spotify Matching & Slug Normalization**
   - Updated `formatSlug` in [`TrackView.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/track-view/TrackView.tsx) to preserve numeric ranges (e.g. `85-92` formatted as `Selected Ambient Works 85-92` instead of splitting with spaces).
   - Updated `normalizeForMatch` in [`urlResolver.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts) and `_normalize` in [`spotapi-service/main.py`](file:///Users/matt/projects/music-cross-linker/spotapi-service/main.py) to preserve hyphenated number ranges consistently across search queries and candidate names.

4. **"See Search Results" for Non-Confident Matches**
   - Modified [`PlatformButton.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/track-view/PlatformButton.tsx) and [`CandidateList.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/track-view/CandidateList.tsx): Removed the `!isNoMatch` gate so candidate picker options remain accessible when no match was automatically found.
   - Set toggle text to `"See search results"` in no-match states and configured automatic search execution upon opening when operating without candidates. Filtered out `*_fallback` placeholder items from candidate cards.

5. **Verification & Build**
   - Tested Next.js production build (`bun run build`) with zero TypeScript or build errors.
   - Pushed all changes via auto-commit.

All tasks are completed and all changes have been pushed to the remote repository. You can access the thread transcript at .

---
