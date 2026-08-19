---
title: "Fix two bugs:"
date: "2026-08-10"
conversation_id: "74de5d3b-3518-474c-b512-cb7583ce2818"
source: "antigravity"
---

# Fix two bugs:

## User

Fix two bugs:

1. In `app/[artist]/[track]/page.tsx`:
Remove the duplicate `{videoId && (<div className="player-wrapper">...</div>)}` block so there is ONLY ONE YouTube embed rendered on the page!

2. In `app/lib/urlResolver.ts`:
Fix the check in `getPlatformLinks` when `src` is present. Previously when `src` was an Apple Music link, `spotifyUrl` was NOT populated by Odesli because `const odesli = await fetchOdesliByUrl(src)` was only filling `spotifyUrl` if `!spotifyUrl`, BUT `fetchOdesliByUrl(src)` MUST be called to retrieve cross-platform URLs!

Specifically in `app/lib/urlResolver.ts`:
```ts
import { fetchOdesliByUrl } from './odesli';

export async function getPlatformLinks(
  artist: string,
  title: string,
  type: 'track' | 'album',
  src?: string
) {
  console.log('[PLATFORM RESOLVER INPUT]', { artist, title, type, src });
  let appleUrl = '';
  let spotifyUrl = '';
  let youtubeUrl = '';

  if (src) {
    if (src.includes('music.apple.com')) {
      appleUrl = src;
    } else if (src.includes('spotify.com')) {
      spotifyUrl = src;
    } else if (src.includes('youtube.com') || src.includes('youtu.be')) {
      youtubeUrl = src;
    }

    const odesli = await fetchOdesliByUrl(src);
    if (odesli) {
      if (!appleUrl && odesli.appleUrl) appleUrl = odesli.appleUrl;
      if (!spotifyUrl && odesli.spotifyUrl) spotifyUrl = odesli.spotifyUrl;
      if (!youtubeUrl && odesli.youtubeUrl) youtubeUrl = odesli.youtubeUrl;
    }
  }

  // If we still don't have Spotify or Apple, try Odesli with artist and title search if needed, or DuckDuckGo / iTunes API search
  if (!appleUrl) {
    try {
      const entity = type === 'album' ? 'album' : 'song';
      const res = await fetch(
        `https://itunes.apple.com/search?term=${encodeURIComponent(
          artist + ' ' + title
        )}&entity=${entity}&limit=1`
      );
      const data = await res.json();
      if (data.results && data.results.length > 0) {
        appleUrl =
          data.results[0].collectionViewUrl ||
          data.results[0].trackViewUrl ||
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
      const regex = new RegExp(`open\\.spotify\\.com\\/${searchType}\\/([a-zA-Z0-9]+)`);
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

Apply these edits now.

---

## Assistant

The user requested edits to files located in `app/[artist]/[track]/page.tsx` and `app/lib/urlResolver.ts`. However, after investigating the project structure at `/Users/matt/projects/external/hermes-webui`, I have confirmed that these directories and files do not exist in the specified location. The project appears to be a backend-heavy structure containing `api/`, `static/`, and `tests/`, but not a standard Next.js

---
