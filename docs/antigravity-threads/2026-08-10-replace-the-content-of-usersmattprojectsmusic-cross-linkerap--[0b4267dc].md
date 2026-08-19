---
title: "Replace the content of `/Users/matt/projects/music-cross-linker/app/li"
date: "2026-08-10"
conversation_id: "0b4267dc-3725-4dc3-a23a-dce7156f7ec8"
source: "antigravity"
---

# Replace the content of `/Users/matt/projects/music-cross-linker/app/li

## User

Replace the content of `/Users/matt/projects/music-cross-linker/app/lib/odesli.ts` with this exact implementation:

```ts
export interface OdesliResult {
  title?: string;
  artistName?: string;
  thumbnailUrl?: string;
  appleUrl?: string;
  spotifyUrl?: string;
  youtubeUrl?: string;
  type?: 'track' | 'album';
  originalUrl?: string;
}

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

    // Fallback for Apple Music URLs when song.link rate-limits (HTTP 429)
    if (sourceUrl.includes('music.apple.com')) {
      const urlParts = sourceUrl.split('?')[0].split('/');
      const lastPart = urlParts[urlParts.length - 1];
      const match = lastPart.match(/(?:id)?(\d+)/);
      const id = match ? match[1] : null;

      if (id) {
        const lookupRes = await fetch(`https://itunes.apple.com/lookup?id=${id}`);
        if (lookupRes.ok) {
          const lookupData = await lookupRes.json();
          const item = lookupData?.results?.[0];
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
      }
    }
  } catch (e) {
    console.error('Odesli API lookup failed:', e);
  }
  return null;
}
```

---
