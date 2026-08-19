---
title: "In `/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts`:"
date: "2026-08-10"
conversation_id: "8c1db351-5c5b-4ad0-8694-e901509f0045"
source: "antigravity"
---

# In `/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts`:

## User

In `/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts`:

Fix `getPlatformLinks(artist: string, title: string, sourceUrl?: string)` so that:
IF `sourceUrl` is passed, ALWAYS use `sourceUrl` directly for that platform, AND pass `sourceUrl` to Odesli to get cross-platform matches!

Specifically:
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

  // Only if appleUrl is STILL missing, search iTunes
  if (!appleUrl) {
    try {
      const countryMatch = sourceUrl?.match(/music\.apple\.com\/([a-z]{2})\//);
      const country = countryMatch ? countryMatch[1] : 'us';
      const albumRes = await fetch(
        `https://itunes.apple.com/search?term=${encodeURIComponent(
          artist + ' ' + title
        )}&entity=album&limit=1&country=${country}`
      );
      const albumData = await albumRes.json();
      if (
        albumData.results &&
        albumData.results.lengt
<truncated 333 bytes>
ryMatch = sourceUrl?.match(/music\.apple\.com\/([a-z]{2})\//);
      const country = countryMatch ? countryMatch[1] : 'us';
      const songRes = await fetch(
        `https://itunes.apple.com/search?term=${encodeURIComponent(
          artist + ' ' + title
        )}&entity=song&limit=1&country=${country}`
      );
      const songData = await songRes.json();
      if (songData.results && songData.results.length > 0) {
        appleUrl = songData.results[0].trackViewUrl || '';
      }
    } catch (e) {
      console.error('iTunes song lookup error:', e);
    }
  }

  // Fallbacks if Odesli/sourceUrl didn't yield Spotify
  if (!spotifyUrl) {
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

The file `/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts` has been updated with the requested logic for `getPlatformLinks`. It now correctly prioritizes the platform of the `sourceUrl` and uses `fetchOdesliByUrl(sourceUrl)` to retrieve cross-platform matches when a `sourceUrl` is provided.

---
