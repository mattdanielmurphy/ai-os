---
title: "Update `/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts"
date: "2026-08-10"
conversation_id: "6f39ed9f-0b58-4a46-b840-66e17b731e2b"
source: "antigravity"
---

# Update `/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts

## User

Update `/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts` to properly resolve direct Spotify URLs:

1. When `sourceUrl` is passed and `sourceUrl` is an Apple Music link, fetch Odesli `fetchOdesliByUrl(sourceUrl)` FIRST!
2. If `odesli.spotifyUrl` is present, use `spotifyUrl = odesli.spotifyUrl`!
3. If `odesli.spotifyUrl` is missing (e.g. because Odesli returned only Apple Music), use iTunes API lookup to find the `collectionViewUrl` (or `trackViewUrl`), and query Odesli with THAT `collectionViewUrl` to get the direct Spotify URL!
4. If still missing, try Spotify Web API via `process.env.SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` (from `app/lib/spotify.ts` or search endpoint) OR DuckDuckGo search fallback!

Update `/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts`:
```ts
import { fetchOdesliByUrl } from './odesli';

export async function getPlatformLinks(
  artist: string,
  title: string,
  sourceUrl?: string
) {
  console.log('[PLATFORM RESOLVER INPUT]', { artist, title, sourceUrl });
  let appleUrl = '';
  let spotifyUrl = '';
  let youtubeUrl = '';
  let isAlbum = false;

  if (sourceUrl) {
    if (sourceUrl.includes('music.apple.com')) {
      appleUrl = sourceUrl;
    } else if (sourceUrl.includes('spotify.com')) {
      spotifyUrl = sourceUrl;
    } else if (sourceUrl.includes('youtube.com') || sourceUrl.includes('youtu.be')) {
      youtubeUrl = sourceUrl;
    }

    const odesli = await fetchOdesliByUrl(sourceUrl);
    if (odesli) {
      if (!appleUrl && odesli.appleUrl) appleUrl = odesli.appleUrl;
      if (!spotifyUrl && odesli.spotifyUrl) spotifyUrl = odesli.spotifyUrl;
      if (!youtubeUrl && odesli.youtubeUrl) youtubeUrl = odesli.youtubeUrl;
      if (odesli.type === 'album') isAlbum = true;
    }
  }

  // Clean up any geo.music.apple.com in appleUrl if returned from Odesli
  if (appleUrl && appleUrl.includes('geo.music.apple.com')) {
    appleUrl = appleUrl.replace('geo.music.apple.com', 'music.apple.com');
  }

  // If appleUrl is missing, search iTune
<truncated 2708 bytes>
search?q=${encodeURIComponent(
              artist + ' ' + title
            )}&type=${searchType}&limit=1`,
            { headers: { Authorization: `Bearer ${tokenData.access_token}` } }
          );
          const spotifySearchData = await spotifySearchRes.json();
          const items = isAlbum ? spotifySearchData.albums?.items : spotifySearchData.tracks?.items;
          if (items && items.length > 0) {
            spotifyUrl = items[0].external_urls?.spotify || '';
          }
        }
      }
    } catch (e) {
      console.error('Spotify API search failed:', e);
    }
  }

  if (!spotifyUrl && !sourceUrl?.includes('spotify.com')) {
    try {
      const searchType = isAlbum ? 'album' : 'track';
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
      const regex = new RegExp(`open\\.spotify\\.com\\/${searchType}\\/([a-zA-Z0-9]+)`);
      const match = html.match(regex);
      if (match && match[1]) {
        spotifyUrl = `https://open.spotify.com/${searchType}/${match[1]}`;
      }
    } catch (e) {
      console.error('Failed to resolve direct Spotify link via search lookup:', e);
    }
  }

  if (!appleUrl) {
    appleUrl = `https://music.apple.com/search?term=${encodeURIComponent(
      artist + ' ' + title
    )}`;
  }
  if (!spotifyUrl) {
    spotifyUrl = `https://open.spotify.com/search/${encodeURIComponent(
      artist + ' ' + title
    )}`;
  }

  return { appleUrl, spotifyUrl, youtubeUrl, isAlbum };
}
```

Apply this edit to `/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts` now!

---

## Assistant

The `/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts` file has been updated to resolve Spotify URLs more effectively, especially when starting with an Apple Music link.

The updated logic now:
1.  **Prioritizes Odesli** when an Apple Music source URL is provided.
2.  **Chains lookups**: If Odesli does not return a Spotify URL, it attempts to use the iTunes API to get a canonical link (based on artist/title), and re-queries Odesli with that canonical URL to maximize the chance of finding the Spotify

---
