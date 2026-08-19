---
title: "Refactor Database Query Logic"
date: "2026-08-13"
conversation_id: "98d8e028-795a-4c59-95c4-f031e31dfa4b"
source: "antigravity"
---

# Refactor Database Query Logic

## User

In /Users/matt/projects/music-cross-linker:
1. Update `app/lib/urlResolver.ts`:
   - Change `SELECT id, artwork_url FROM resolved_entities` to `SELECT id FROM resolved_entities` (line 343).
   - In `resolved_entities` table, `artwork_url` column does not exist or we do not have ALTER privileges on `resolved_entities` in production DB. `artwork_url` is stored in `entity_matches` and `match_candidates` instead!
   - Remove `artworkUrl = byFingerprint[0].artwork_url;` and safely select `artwork_url` from `entity_matches` or query `match_candidates` / `resolveArtworkImage`.

Check that `bun run build` passes cleanly after editing.

---

## Assistant

The requested changes to [`app/lib/urlResolver.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts) have been successfully implemented:

- Updated the SQL query on line 343 to select only `id` from `resolved_entities`.
- Replaced the assignment of `artworkUrl` with a call to [`resolveArtworkImage`](file:///Users/matt/projects/music-cross-linker/app/lib/artwork.ts#L3-L33) (imported from [`artwork.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/artwork.ts)).
- Verified that `bun run build` completes successfully.

---
