---
title: "Fix Explicit Link Confidence"
date: "2026-08-13"
conversation_id: "39d7ccdb-cda6-4b8a-a4ba-4178c7f11541"
source: "antigravity"
---

# Fix Explicit Link Confidence

## User

In `app/lib/urlResolver.ts`, fix the explicit link source candidate confidence bug.

When `sourceUrl` is explicitly provided as the source link (e.g. `ctx.sourcePlatform === 'apple_music' && sourceUrl`), update or insert `match_candidates` with `confidence = 1` and `source = 'explicit'`.

Specifically:
1. In `resolveApplePlatform`:
   ```typescript
   if (ctx.sourcePlatform === 'apple_music' && sourceUrl) {
     const meta = await fetchAppleMusicMetadata(sourceUrl);
     const existing = await sql`SELECT id FROM match_candidates WHERE entity_id = ${entityId} AND platform = 'apple_music' AND candidate_url = ${sourceUrl} LIMIT 1`;
     let candidateId = existing[0]?.id;
     if (!candidateId) {
       const inserted = await sql`
         INSERT INTO match_candidates (entity_id, platform, candidate_url, title, artist, thumbnail_url, rank, source, confidence)
         VALUES (${entityId}, 'apple_music', ${sourceUrl}, ${meta.title}, ${meta.artist}, ${meta.thumbnail_url}, 1, 'explicit', 1)
         RETURNING id
       `;
       candidateId = inserted[0].id;
     } else {
       await sql`
         UPDATE match_candidates SET confidence = 1, source = 'explicit' WHERE id = ${candidateId}
       `;
     }
     await sql`
       INSERT INTO entity_matches (entity_id, platform, matched_url, matched_by, candidate_id, updated_at, uncertain)
       VALUES (${entityId}, 'apple_music', ${sourceUrl}, 'auto', ${candidateId || null}, now(), false)
       ON CONFLICT (entity_id, platform) DO UPDATE
         SET matched_url = EXCLUDED.matched_url, matched_by = 'auto', candidate_id = EXCLUDED.candidate_id, updated_at = now(), uncertain = false
     `;
     const candidates = await sql`SELECT * FROM match_candidates WHERE entity_id = ${entityId} AND platform = 'apple_music' ORDER BY rank ASC`;
     return { url: sourceUrl, matchedBy: 'explicit', candidates, uncertain: false };
   }
   ```

2. Do the exact same candidate update in `resolveSpotifyPlatform`:
   ```typescript
   if (ctx.sourcePlatform === 'spotify' && source
<truncated 1410 bytes>
atchedBy: 'explicit', candidates, uncertain: false };
   }
   ```

3. Do the exact same candidate update in `resolveYoutubePlatform`:
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
     } else {
       await sql`
         UPDATE match_candidates SET confidence = 1, source = 'explicit' WHERE id = ${candidateId}
       `;
     }
     await sql`
       INSERT INTO entity_matches (entity_id, platform, matched_url, matched_by, candidate_id, updated_at, uncertain)
       VALUES (${entityId}, 'youtube', ${sourceUrl}, 'auto', ${candidateId || null}, now(), false)
       ON CONFLICT (entity_id, platform) DO UPDATE
         SET matched_url = EXCLUDED.matched_url, matched_by = 'auto', candidate_id = EXCLUDED.candidate_id, updated_at = now(), uncertain = false
     `;
     const candidates = await sql`SELECT * FROM match_candidates WHERE entity_id = ${entityId} AND platform = 'youtube' ORDER BY rank ASC`;
     return { url: sourceUrl, matchedBy: 'explicit', candidates, uncertain: false };
   }
   ```

Apply these edits to `app/lib/urlResolver.ts`.

---

## Assistant

The fix for the explicit link source candidate confidence bug has been applied to `app/lib/urlResolver.ts`. The `match_candidates` table is now correctly updated with `confidence = 1` and `source = 'explicit'` when an explicit `sourceUrl` is provided for Apple Music, Spotify, and YouTube, ensuring that these explicitly matched candidates are correctly prioritized.

---
