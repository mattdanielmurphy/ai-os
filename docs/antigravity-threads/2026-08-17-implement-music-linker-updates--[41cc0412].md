---
title: "Implement Music Linker Updates"
date: "2026-08-17"
conversation_id: "41cc0412-e792-4cb6-9015-2d4ae10515e0"
source: "antigravity"
---

# Implement Music Linker Updates

## User

Please make the following surgical code updates in music-cross-linker:

1. Create `app/components/track-view/TypeBadge.tsx`:
A client component ('use client') that renders the badge in the track header.
Props: { isAlbum: boolean; typeHint?: 'album' | 'track' | null }
Features:
- Renders badge showing "Album Link" if isAlbum is true, or "Track Link" if isAlbum is false.
- Has a subtle interactive toggle or link (e.g. title="Click to toggle Track / Album link", onClick or href using next/navigation useRouter/useSearchParams or a link with ?type=track / ?type=album) allowing the user to switch between Album and Track mode with 1 click.

2. Update `app/components/track-view/TrackView.tsx`:
- Fix slug formatting regex in `formatSlug`: Change `.split(/(?<!\d)-(?!\d)/)` to `.split('-').filter(Boolean)`. This ensures `alive-2007` becomes `Alive 2007` and `daft-punk` becomes `Daft Punk`.
- Accept `typeHint?: 'album' | 'track' | null` in props (from searchParams or params).
- Pass `typeHint` to `resolveEntity(a, t, country || 'CA', sourceUrl, typeHint)`.
- Use `ctx.canonicalTitle` (if available and clean) as `displaySource` / `displayPrimary`, and `ctx.canonicalArtist` (if available) as `displaySecondary`, falling back to `t` and `a`.
- Replace the static `<div className="badge">{ctx.isAlbum ? 'Album Link' : 'Track Link'}</div>` with `<TypeBadge isAlbum={ctx.isAlbum} typeHint={typeHint} />`.

3. Update `app/[...url]/page.tsx`:
- Support prefix routes `/album/[artist]/[track]` (3 segments where segment 0 is 'album') and `/track/[artist]/[track]` (3 segments where segment 0 is 'track').
- Extract `typeHint` from `resolvedSearchParams?.type` (if 'album' or 'track') or from `urlSegments[0]` (if 'album' or 'track').
- Pass `typeHint` to `TrackView`.

4. Update `app/lib/urlResolver.ts`:
- In `EntityContext`:
  Add `canonicalTitle?: string | null;`
  Add `canonicalArtist?: string | null;`
  Add `typeHint?: 'album' | 'track' | null;`
- In `resolveEntity(artist: string, title: string, country: string, sourceUrl?: string, typeHint?: 'album' | 'track' | null)`:
  - If `typeHint === 'album'`, `isAlbum = true`.
  - If `typeHint === 'track'`, `isAlbum = false`.
  - If neither, check title for common album patterns (e.g. `/(?:^|\s)(?:full\s+album|alive\s+\d{4}|live\s+at\s+)(?:$|\s)/i.test(cleanTitle)`).
  - When querying existing `entityId`:
    - Check if cached matches or high-confidence candidates (`WHERE entity_id = ${entityId} AND candidate_url LIKE '%/album/%'`) exist. If so, set `isAlbum = true`.
    - Retrieve `canonicalTitle` and `canonicalArtist` from `match_candidates` (`SELECT title, artist FROM match_candidates WHERE entity_id = ${entityId} AND title IS NOT NULL AND confidence = 1 ORDER BY rank ASC LIMIT 1`).
  - Return `canonicalTitle` and `canonicalArtist` in `EntityContext`.
- In `resolveApplePlatform` and `resolveSpotifyPlatform`:
  - Preserve all existing `spotapi-service` constraints (never use official Spotify Web API).
  - When a high confidence album match is found (`collectionViewUrl?.includes('/album/')` or SpotAPI album result), if `ctx.isAlbum` was false, update `ctx.isAlbum = true`.

Ensure all files compile cleanly and no syntax errors are introduced.

---

## Assistant

The requested surgical code updates have been applied successfully:

1.  **Created `app/components/track-view/TypeBadge.tsx`**: A client component for toggling between Album and Track modes in the track header.
2.  **Updated `app/components/track-view/TrackView.tsx`**:
    *   Improved slug formatting regex to `.split('-').filter(Boolean)`.
    *   Added `typeHint` support and passed it to `resolveEntity`.
    *   Updated to display `ctx.canonicalTitle` and `ctx.canonicalArtist` if available.
    *   Replaced the static badge with the new `TypeBadge`.
3.  **Updated `app/[...url]/page.tsx`**: Added support for `/album/` and `/track/` route prefixes and extracted `typeHint` for the `TrackView` component.
4.  **Updated `app/lib/urlResolver.ts`**:
    *   Extended `EntityContext` with `canonicalTitle`, `canonicalArtist`, and `typeHint`.
    *   Updated `resolveEntity` to prioritize `typeHint`, check for album patterns in titles, and query `match_candidates` for canonical metadata and album confirmation.
    *   Ensured platform resolvers (Spotify/Apple) respect the `isAlbum` status and detection logic.

All changes are integrated and maintain the required functionality.

---
