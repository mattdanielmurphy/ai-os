---
title: "Fix Url Match Resolution Bug"
date: "2026-08-13"
conversation_id: "1447e88b-4513-4b25-b9ff-ee8813f69269"
source: "antigravity"
---

# Fix Url Match Resolution Bug

## User

In `app/lib/urlResolver.ts`, fix the bug where an explicit source link still reports a cached or low-confidence match state.

Specifically:
1. In `saveAutoMatch(entityId: string, platform: Platform, url: string, candidateId?: string | null)`:
   When `saveAutoMatch` is called for an explicit source link or fresh auto match, ensure `uncertain = false` and `matched_by = 'auto'` (or `'explicit'`) by updating the `ON CONFLICT` clause:
   ```typescript
   async function saveAutoMatch(entityId: string, platform: Platform, url: string, candidateId?: string | null) {
     await sql`
       INSERT INTO entity_matches (entity_id, platform, matched_url, matched_by, candidate_id, updated_at, uncertain)
       VALUES (${entityId}, ${platform}, ${url}, 'auto', ${candidateId || null}, now(), false)
       ON CONFLICT (entity_id, platform) DO UPDATE
         SET matched_url = EXCLUDED.matched_url, candidate_id = EXCLUDED.candidate_id, updated_at = now(), uncertain = false
         WHERE entity_matches.matched_by <> 'manual'
     `;
   }
   ```

2. In `resolveApplePlatform`, `resolveSpotifyPlatform`, and `resolveYoutubePlatform`:
   When `ctx.sourcePlatform === '<platform>' && sourceUrl`, also clear any manual/uncertain match in `entity_matches` for this platform if `sourceUrl` is explicitly provided as the source link:
   ```typescript
   await sql`
     INSERT INTO entity_matches (entity_id, platform, matched_url, matched_by, candidate_id, updated_at, uncertain)
     VALUES (${entityId}, 'apple_music', ${sourceUrl}, 'auto', ${candidateId || null}, now(), false)
     ON CONFLICT (entity_id, platform) DO UPDATE
       SET matched_url = EXCLUDED.matched_url, matched_by = 'auto', candidate_id = EXCLUDED.candidate_id, updated_at = now(), uncertain = false
   `;
   ```
   Do the same for Spotify (`resolveSpotifyPlatform`) and YouTube (`resolveYoutubePlatform`).

Let's check `resolveApplePlatform` lines 399-414:
```typescript
  if (ctx.sourcePlatform === 'apple_music' && sourceUrl) {
    const meta = await fetchAppleMus
<truncated 2707 bytes>
uncertain: false };
  }
```

Check `resolveYoutubePlatform` lines 525-545:
```typescript
  if (ctx.sourcePlatform === 'youtube' && sourceUrl) {
    let yTitle = null, yThumbnail = null;
    try {
      const oembed = await fetch(`https://www.youtube.com/oembed?url=${encodeURIComponent(sourceUrl)}&format=json`).then(r => r.json());
      yTitle = cleanYouTubeTitle(oembed.title);
      yThumbnail = oembed.thumbnail_url;
    } catch (e) {}
    const existing = await sql`SELECT id FROM match_candidates WHERE entity_id = ${entityId} AND platform = 'youtube' AND candidate_url = ${sourceUrl} LIMIT 1`;
    let candidateId = existing[0]?.id;
    if (!candidateId) {
      const inserted = await sql`
        INSERT INTO match_candidates (entity_id, platform, candidate_url, title, thumbnail_url, rank, source, confidence)
        VALUES (${entityId}, 'youtube', ${sourceUrl}, ${yTitle}, ${yThumbnail}, 1, 'explicit', 1)
        RETURNING id
      `;
      candidateId = inserted[0].id;
    }
    await sql`
      INSERT INTO entity_matches (entity_id, platform, matched_url, matched_by, candidate_id, updated_at, uncertain)
      VALUES (${entityId}, 'youtube', ${sourceUrl}, 'auto', ${candidateId || null}, now(), false)
      ON CONFLICT (entity_id, platform) DO UPDATE
        SET matched_url = EXCLUDED.matched_url, matched_by = EXCLUDED.matched_by, candidate_id = EXCLUDED.candidate_id, updated_at = now(), uncertain = false
    `;
    const candidates = await sql`SELECT * FROM match_candidates WHERE entity_id = ${entityId} AND platform = 'youtube' ORDER BY rank ASC`;
    return { url: sourceUrl, matchedBy: 'explicit', candidates, uncertain: false };
  }
```

And update `cached.apple_music` / `cached.spotify` in `resolveApplePlatform` and `resolveSpotifyPlatform`:
If `cached.apple_music.url === sourceUrl` or if `matchedBy === 'explicit'`, return `uncertain: false`.

Apply these modifications to `app/lib/urlResolver.ts`.

---

## Assistant

The bug where explicit source links incorrectly reported cached or low-confidence match states has been fixed in `app/lib/urlResolver.ts`.

Key modifications include:

*   **`saveAutoMatch`**: Updated the SQL `INSERT` and `ON CONFLICT` clause to explicitly manage the `uncertain` column, ensuring that new auto-matches are flagged as `uncertain = false` and overrides respect the `matched_by <> 'manual'` constraint.
*   **Platform Resolvers (`resolveApplePlatform`, `resolveSpotifyPlatform`, `resolveYoutubePlatform`)**: 
    *   For explicit source links, I implemented a forced database update to clear any previous manual/uncertain flags for that entity and platform. 
    *   The `PlatformResult` returned now explicitly specifies `uncertain: false` when an explicit URL is used.
*   **Cache Handling**: Updated the cache hit logic to force `uncertain: false` if a cached match matches the current explicit `sourceUrl` or was originally flagged as `'explicit'`.

These changes ensure that explicit user actions (providing a link) correctly supersede any previous low-confidence or manual-override states for that platform.

---
