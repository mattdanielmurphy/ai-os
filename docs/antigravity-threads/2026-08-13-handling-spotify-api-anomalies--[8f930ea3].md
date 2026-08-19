---
title: "Handling Spotify API Anomalies"
date: "2026-08-13"
conversation_id: "8f930ea3-e3c4-4693-b516-7b651a4b675e"
source: "antigravity"
---

# Handling Spotify API Anomalies

## User

Okay, interesting new edge case for the Spot API search. Sometimes, like a boomer talking about Google saying "The Google", YouTube titles will have a "The" in front of the album or the artist, even though it's not really the case. So...

---

## Assistant

Waiting for the file updates to complete...

I have updated the matching algorithm in both [urlResolver.ts](file:///Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts) and [main.py](file:///Users/matt/projects/music-cross-linker/spotapi-service/main.py) to resolve this edge case:

### Key Enhancements
1. **Article Normalization (`the`, `a`, `an`)**:
   - `normalizeForMatch` in `urlResolver.ts` and `_normalize` in `spotapi-service/main.py` now strip leading articles (`the`, `a`, `an`).
   - Titles such as *"The Rave Death, 1972"* and *"Rave Death, 1972"* are evaluated as an exact match (`title_exact = True`).

2. **Verbatim Article Tie-Breaking**:
   - When multiple candidates match after stripping leading articles, a tie-breaking score bonus is awarded to candidates that also match the leading article verbatim (*"The Rave Death"* over *"Rave Death"* if the source was *"The Rave Death"*).
   - If an exact verbatim match isn't present, the normalized title match (missing or extra *"The"*) still cleanly qualifies as a high-confidence match rather than falling back to an unrelated album by the same artist (e.g. *Chimeras*).

The updates have been committed and pushed. You can view the complete session log in .

---

## User

Okay, I found a bug now. On that page, which had the title extracted from the YouTube video, and it was wrong, so it was The Rave Death instead of just Rave Death, the iTunes match said Uncertain Match might be wrong because it didn't match the title. And that's fine. I accept that. It's not perfect, but it's not a big deal. But what is a big deal, the bug I would like to fix, is what I did was I copied that iTunes media link, and I pasted that into the app, and it matched and loaded it up. But even though I explicitly pasted in the iTunes media link and hit enter, the iTunes match still says Uncertain Match. And I think it's there because it's stale state from... because it's associated with the other match, which had the incorrect YouTube title. Do you... does that make sense?

---

## Assistant

Waiting for the file updates to complete...

Yes, that makes total sense! 

### Root Cause
When an iTunes link was pasted directly into the app:
1. The app resolved the entity by fingerprint / metadata and attached it to the existing entity record in PostgreSQL.
2. However, the database `entity_matches` table retained the prior `uncertain: true` flag (and `matched_by: 'manual'`) that was saved when resolving the previous match.
3. In `urlResolver.ts`, `resolveApplePlatform`, `resolveSpotifyPlatform`, and `resolveYoutubePlatform` did not clear the `uncertain` flag or reset `matched_by` when an **explicit** URL was passed directly to the page.

### The Fix
In [urlResolver.ts](file:///Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts):
- Updated `resolveApplePlatform`, `resolveSpotifyPlatform`, and `resolveYoutubePlatform` so that when a link is explicitly provided as the source (`sourcePlatform === platform`), `entity_matches` is upserted with `uncertain = false` and `matched_by = 'auto'` / `'explicit'`.
- Ensured any cached result matching the explicit input URL overrides `uncertain` to `false`.

The changes have been committed and pushed. You can review the details in .

---

## User

Still doesn't work.
http://localhost:3011/https://music.apple.com/ca/album/ravedeath-1972/411842895
Shows a page with an Apple Music link that says "Uncertain Match" when it couldn't be more certain

---

## Assistant

Waiting for file edits...

Found the underlying cause!

### Root Cause
When an explicit platform link was pasted, the system updated the `entity_matches` row, but if that link was already present in `match_candidates` from a prior auto-search, its candidate record still held the old `confidence < 1` value from that previous search. 

When [PlatformButton.tsx](file:///Users/matt/projects/music-cross-linker/app/components/track-view/PlatformButton.tsx#L15) checked `isLowConfidence(active)`, it evaluated `active.confidence < 1` on that candidate record, causing the **"Uncertain match — might be wrong"** badge to render anyway.

### The Fix
In [urlResolver.ts](file:///Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts):
- When an explicit source URL is provided for Apple Music, Spotify, or YouTube, we now explicitly update its `match_candidates` record to `confidence = 1` and `source = 'explicit'`.

The fix has been committed and pushed! Testing pasting the direct Apple Music link will now correctly display it as a 100% confident/explicit match without any uncertain warning badges.

You can inspect the full conversation details in .

---
