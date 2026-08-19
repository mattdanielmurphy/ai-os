---
title: "Update app/lib/odesli.ts so that fetchOdesliByUrl returns the raw sour"
date: "2026-08-10"
conversation_id: "b8dd5dd2-c4c6-466a-9563-49c00e551550"
source: "antigravity"
---

# Update app/lib/odesli.ts so that fetchOdesliByUrl returns the raw sour

## User

Update app/lib/odesli.ts so that fetchOdesliByUrl returns the raw source link passed in for the matching platform (if applicable) or cleans up Geo links, and updates app/lib/urlResolver.ts to prioritize exact source URLs passed in for Apple Music, Spotify, YouTube, etc.

Specifically:
1. In `app/lib/odesli.ts`:
```ts
export interface OdesliResult {
  title?: string;
  artistName?: string;
  thumbnailUrl?: string;
  appleUrl?: string;
  spotifyUrl?: string;
  youtubeUrl?: string;
  type?: 'track' | 'album';
}

export async function fetchOdesliByUrl(sourceUrl: string): Promise<OdesliResult | null> {
  try {
    const res = await fetch(
      `https://api.song.link/v1-alpha.1/links?url=${encodeURIComponent(sourceUrl)}`
    );
    if (!res.ok) return null;
    const data = await res.json();
    
    const entityId = data.entityUniqueId;
    const entity = data.entitiesByUniqueId?.[entityId];
    
    let appleUrl = data.linksByPlatform?.appleMusic?.url || data.linksByPlatform?.itunes?.url;
    let spotifyUrl = data.linksByPlatform?.spotify?.url;
    let youtubeUrl = data.linksByPlatform?.youtube?.url || data.linksByPlatform?.youtubeMusic?.url;

    // Clean up geo.music.apple.com links if needed
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
    };
  } catch (e) {
    console.error('Odesli API lookup failed:', e);
    return null;
  }
}
```

2. In `app/lib/urlResolver.ts`:
Update `getPlatformLinks` to preserve exact user source link when passed:
```ts
import { fetchOdesliByUrl } from './odesli';

export async function getPlatformLinks(
  artist: string,
  title: string,
  type: 'track' | 'album',
  src?: string
) {
  console.log('[PLATFORM RESOLVER INPUT]', { artist, title, ty
<truncated 1097 bytes>
    '';
      }
    } catch (e) {
      console.error('Failed to resolve Apple Music link:', e);
    }
  }

  if (!appleUrl) {
    appleUrl = `https://music.apple.com/search?term=${encodeURIComponent(
      artist + ' ' + title
    )}`;
  }

  if (!spotifyUrl) {
    try {
      const searchType = type === 'album' ? 'album' : 'track';
      const query = `site:open.spotify.com/${searchType} ${artist} ${title}`;
      const res = await fetch(
        `https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`,
        {
          headers: {
            'User-Agent':
              'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          },
        }
      );
      const html = await res.text();
      const regex = new RegExp(`open\\\\.spotify\\\\.com\\\\/${searchType}\\\\/([a-zA-Z0-9]+)`);
      const match = html.match(regex);
      if (match && match[1]) {
        spotifyUrl = `https://open.spotify.com/${searchType}/${match[1]}`;
      }
    } catch (e) {
      console.error('Failed to resolve direct Spotify link via search lookup:', e);
    }
  }

  if (!spotifyUrl) {
    spotifyUrl = `https://open.spotify.com/search/${encodeURIComponent(
      artist + ' ' + title
    )}`;
  }

  return { appleUrl, spotifyUrl, youtubeUrl };
}
```

3. Update `app/[...url]/page.tsx`:
Ensure `src` parameter is passed along to `/${slugify(artist)}/${slugify(title)}?type=${type}&src=${encodeURIComponent(url)}` when redirecting, so `TrackPage` receives the source URL!

4. Update `app/[artist]/[track]/page.tsx`:
Accept `src` searchParam and pass it to `getPlatformLinks(a, t, type, src)`.
Also, if `src` is a YouTube link or `youtubeUrl` is resolved directly, use it / embed it directly instead of falling back to YouTube search results. If `src` was pasted directly, respect that exact source URL for its platform!

Modify these files directly now.

---

## Assistant

All requested changes have been applied to the `music-cross-linker` project.

- **`app/lib/odesli.ts`**: `fetchOdesliByUrl` now handles the raw source link and cleans `geo.music.apple.com` links.
- **`app/lib/urlResolver.ts`**: `getPlatformLinks` now prioritizes exact source URLs passed for Apple Music, Spotify, and YouTube.
- **`app/[...url]/page.tsx`**: The `src` parameter is now passed along when redirecting.
- **`app/[artist]/[track]/page.tsx`**: Updated to accept the `src` search parameter and use it to resolve/embed the platform link directly, with a fallback to YouTube search results.

---
