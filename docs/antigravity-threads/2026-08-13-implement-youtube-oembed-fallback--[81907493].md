---
title: "Implement YouTube Oembed Fallback"
date: "2026-08-13"
conversation_id: "81907493-9104-4de5-8d37-c9835eef15b0"
source: "antigravity"
---

# Implement YouTube Oembed Fallback

## User

In `/Users/matt/projects/music-cross-linker/app/api/resolve-link/route.ts`:
Import `fetchOdesliByUrl` from `../../lib/odesli`.

```ts
import { NextRequest, NextResponse } from 'next/server';
import { fetchOdesliByUrl } from '../../lib/odesli';
import { cleanYouTubeTitle, parseYouTubeTitle } from '../../lib/youtube/titleParser';
import { getSlugForUrl } from '../../lib/slugStore';
```

Also, in the `if (videoId && !odesli)` fallback block at the bottom:
Fetch YouTube oEmbed metadata if available, parse it with `parseYouTubeTitle(rawVideoTitle)`, so if Odesli has no match for a brand new YouTube video, it still resolves to a clean slug (`/led-zeppelin/physical-graffiti`) instead of raw video ID slug `/qhjaUsJ8PIk`!

```ts
  if (videoId) {
    let rawVideoTitle: string | null = null;
    try {
      const oembed = await fetch(
        `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${videoId}&format=json`
      ).then((r) => (r.ok ? r.json() : null));
      rawVideoTitle = oembed?.title || null;
    } catch {}

    if (rawVideoTitle) {
      const parsed = parseYouTubeTitle(rawVideoTitle);
      const artistName = parsed.artist || '';
      const title = parsed.title;
      const slug = getSlugForUrl(lookupUrl, title, artistName, videoId);
      return NextResponse.json({ slug });
    }

    const slug = getSlugForUrl(lookupUrl, videoId, '', videoId);
    return NextResponse.json({ slug });
  }
```

Write this to `/Users/matt/projects/music-cross-linker/app/api/resolve-link/route.ts`.

---
