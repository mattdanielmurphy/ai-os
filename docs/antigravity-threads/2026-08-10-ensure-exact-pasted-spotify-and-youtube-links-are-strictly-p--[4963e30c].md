---
title: "Ensure exact pasted Spotify and YouTube links are strictly preserved:"
date: "2026-08-10"
conversation_id: "4963e30c-a73e-4e69-a064-4975e0c75121"
source: "antigravity"
---

# Ensure exact pasted Spotify and YouTube links are strictly preserved:

## User

Ensure exact pasted Spotify and YouTube links are strictly preserved:

1. In `/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts`:
In `getPlatformLinks(artist, title, sourceUrl)`:
Make sure:
```ts
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
```
And verify that if `sourceUrl` contains `spotify.com`, `spotifyUrl` is NEVER overwritten by DuckDuckGo or Spotify search fallback!

2. In `/Users/matt/projects/music-cross-linker/app/[artist]/[track]/page.tsx`:
```ts
  let videoId = null;
  if (youtubeUrl) {
    const ytMatch = youtubeUrl.match(/(?:youtu\.be\/|youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=))([^"&?\/ ]{11})/);
    videoId = ytMatch ? ytMatch[1] : null;
  }
  
  // ONLY run YouTube search if we don't already have a videoId from youtubeUrl (whether from direct pasted YouTube link or Odesli)!
  if (!videoId) {
    const videos = await getTopVideos(a, t, isAlbum ? 'album' : 'track', 5);
    videoId = videos.length > 0 ? videos[0].id : null;
  }
```

Apply these edits to `/Users/matt/projects/music-cross-linker/app/[artist]/[track]/page.tsx` and `/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts` now!

---

## Assistant

The requested updates have been applied to ensure strict preservation of pasted Spotify and YouTube links.

### Summary of Changes

*   **[`urlResolver.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts)**: Modified the Spotify search fallback logic to ensure `spotifyUrl` is not overwritten if a link from `spotify.com` was already provided.
*   **[`page.tsx`](file:///Users/matt/projects/music-cross-linker/app/%5Bartist%5D/%5Btrack%5D/page.tsx)**: Added explicit checks to ensure YouTube search only runs as a fallback if a `videoId` was not already resolved from a provided `youtubeUrl`.

---
