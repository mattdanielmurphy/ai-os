---
title: "Implement Artwork And Palette"
date: "2026-08-13"
conversation_id: "0d1763cd-57f6-47c5-996e-6ad04b6fbd39"
source: "antigravity"
---

# Implement Artwork And Palette

## User

In /Users/matt/projects/music-cross-linker:
1. Create `migrations/005_add_artwork_and_palette.sql`:
   ```sql
   ALTER TABLE match_candidates ADD COLUMN IF NOT EXISTS artwork_url text;
   ALTER TABLE entity_matches ADD COLUMN IF NOT EXISTS artwork_url text;
   ALTER TABLE entity_matches ADD COLUMN IF NOT EXISTS artwork_palette jsonb;
   ```
2. Create `app/lib/artwork.ts`:
   Implement `resolveArtworkImage(artist: string, title: string, sourceUrl?: string)`:
   - If sourceUrl contains `apple.com`, extract album/track ID and hit `https://itunes.apple.com/lookup?id=...` to get `artworkUrl100` upscaled to `1000x1000bb.jpg`.
   - If sourceUrl contains `spotify.com`, hit Spotify oEmbed `https://open.spotify.com/oembed?url=...` to get `thumbnail_url`.
   - Fallback: Hit `https://itunes.apple.com/search?term=${encodeURIComponent(artist ? `${artist} ${title}` : title)}&media=music&entity=album,song&limit=1` to get `artworkUrl100` upscaled to `1000x1000bb.jpg`.
   - Return string URL or null.

3. Update `app/lib/palette.ts`:
   Implement `getPaletteFromImage(imageUrl: string)` using `sharp`:
   - Download buffer, resize to 50x50.
   - Scan pixels, filter out near-black ($R+G+B < 40$ or $R,G,B < 25$) and near-white ($R,G,B > 230$).
   - Cluster or pick 2-3 vibrant RGB colors (e.g. highest saturation $S = (\max - \min) / \max$).
   - If no vibrant pixels found, generate fallback vibrant hues from non-black average or default rich purple/teal gradient.
   - Return `{ '--bg-gradient': 'linear-gradient(135deg, color1, color2, color3)', '--text-primary': ..., '--text-secondary': ..., '--card-bg': 'rgba(0,0,0,0.3)' }`.

4. Update `app/lib/urlResolver.ts` & `app/components/track-view/TrackView.tsx`:
   - In `resolveEntity`, include `artworkUrl` in the returned `EntityContext`.
   - In `TrackView.tsx`, call `resolveArtworkImage` or use `ctx.artworkUrl` on initial render, get palette, and apply style to `.main-content`.

Check that `bun run build` succeeds after editing.

---

## Assistant

Completed requested artwork and palette integration. All changes verified by successful `bun run build`.

---
