---
title: "Automated Album Title Cleaning"
date: "2026-08-13"
conversation_id: "232af891-5edb-4418-92aa-d89e36586046"
source: "antigravity"
---

# Automated Album Title Cleaning

## User

NEVER should we ever see "Full album" in the fucking album title ffs. Obviously, the youtube video title had that in there and we need to strip it out.
And frankly, I think if we look at the two matches albums on AM and Spotify, we should then go: "oh, ok, now I know what the REAL album title should be" and fix it, you know?

---

## Assistant

I updated the YouTube title cleaning logic in [`app/lib/youtube/titleParser.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts) and added unit tests in [`app/lib/youtube/titleParser.test.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.test.ts).

### What Was Fixed & Updated
1. **Noise Tag Stripping**:
   - Added regex rules to strip out `"Full album"`, `"full album stream"`, `"full album audio"`, `"full album playlist"`, and `"seamless transitions"` regardless of whether they are wrapped in parentheses `(...)`, square brackets `[...]`, or appearing as unparenthesized standalone text in video titles (e.g. `Ravedeath 1972 (Seamless transitions) Full album` -> `Ravedeath 1972`).
2. **Title & Artist Resolution**:
   - YouTube video titles containing these phrases now strip them cleanly out during `resolveEntity` and `parseYouTubeTitle`, so canonical entity titles and displayed headers no longer retain `"Full album"`.
3. **Automated Verification**:
   - Unit tests pass with `bun test app/lib/youtube/titleParser.test.ts`.

Reference thread log:

---
