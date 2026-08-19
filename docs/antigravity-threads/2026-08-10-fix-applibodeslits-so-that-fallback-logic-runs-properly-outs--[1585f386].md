---
title: "Fix `app/lib/odesli.ts` so that fallback logic runs properly outside t"
date: "2026-08-10"
conversation_id: "1585f386-1cf5-4314-a8f3-4a22786a6f61"
source: "antigravity"
---

# Fix `app/lib/odesli.ts` so that fallback logic runs properly outside t

## User

Fix `app/lib/odesli.ts` so that fallback logic runs properly outside the `if (res.ok)` block.

```ts
export async function fetchOdesliByUrl(sourceUrl: string): Promise<OdesliResult | null> {
  try {
    const res = await fetch(
      `https://api.song.link/v1-alpha.1/links?url=${encodeURIComponent(sourceUrl)}`
    );

    if (res.ok) {
      const data = await res.json();
      const entityId = data.entityUniqueId;
      const entity = data.entitiesByUniqueId?.[entityId];
      let appleUrl = data.linksByPlatform?.appleMusic?.url || data.linksByPlatform?.itunes?.url;
      let spotifyUrl = data.linksByPlatform?.spotify?.url;
      let youtubeUrl = data.linksByPlatform?.youtube?.url || data.linksByPlatform?.youtubeMusic?.url;

      if (appleUrl && appleUrl.includes('geo.music.apple.com')) {
        appleUrl = appleUrl.replace('geo.music.apple.com', 'music.apple.com');
      }

      return {
        title: entity?.title,
        artistName: entity?.artistName,
        thumbnailUrl: entity?.thumbnailUrl,
        type: entity?.type === 'album' ? 'album' : 'track',
        appleUrl,
        spotifyUrl,
        youtubeUrl,
        originalUrl: sourceUrl,
      };
    }
  } catch (e) {
    console.error('Odesli API lookup failed:', e);
  }

  // Fallback for Apple Music URLs when song.link rate-limits (HTTP 429) or fails
  if (sourceUrl.includes('music.apple.com')) {
    try {
      const urlStr = sourceUrl.replace(/^(https?:\/+)/, 'https://');
      const url = new URL(urlStr);
      const pathParts = url.pathname.split('/');
      const id = pathParts.find((part) => /^\d+$/.test(part) || part.startsWith('id'))?.replace('id', '');
      
      if (id) {
        const lookup = await fetch(`https://itunes.apple.com/lookup?id=${id}`)
          .then((r) => (r.ok ? r.json() : null))
          .catch(() => null);

        const item = lookup?.results?.[0];
        if (item) {
          return {
            title: item.collectionName || item.trackName,
            artistName: item.artistName,
            type: item.wrapperType === 'collection' ? 'album' : 'track',
            appleUrl: item.collectionViewUrl || item.trackViewUrl,
            originalUrl: sourceUrl,
          };
        }
      }
    } catch (e) {
      console.error('Apple Music fallback error:', e);
    }
  }

  return null;
}
```

Target File: /Users/matt/projects/music-cross-linker/app/lib/odesli.ts

---

## Assistant

I have successfully refactored `app/lib/odesli.ts`. The primary Odesli API call is now contained within its own `try-catch` block, and the Apple Music fallback logic has been moved outside of that block. This ensures that the fallback will execute even if the Odesli request fails, returns a non-OK status, or throws an error.

The changes have been verified and I have reported the completion to the parent agent.

---
