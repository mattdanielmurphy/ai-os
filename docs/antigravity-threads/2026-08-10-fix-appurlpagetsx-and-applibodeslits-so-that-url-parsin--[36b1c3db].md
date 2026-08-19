---
title: "Fix `app/[...url]/page.tsx` and `app/lib/odesli.ts` so that URL parsin"
date: "2026-08-10"
conversation_id: "36b1c3db-ef53-4c01-b4be-793793cc191e"
source: "antigravity"
---

# Fix `app/[...url]/page.tsx` and `app/lib/odesli.ts` so that URL parsin

## User

Fix `app/[...url]/page.tsx` and `app/lib/odesli.ts` so that URL parsing and fallbacks work cleanly.

1. In `app/[...url]/page.tsx`:
Fix URL normalization when Next.js collapses multiple slashes in route params:
```ts
let rawUrl = urlSegments.join('/');
// Clean up any mangled protocol like 'https:/music.apple.com' or 'http:/music.apple.com'
rawUrl = rawUrl.replace(/^(https?:\/+)/, '');
rawUrl = 'https://' + rawUrl;
```

2. In `app/lib/odesli.ts`:
Make the Apple Music fallback robust:
```ts
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
```

Target Files:
- /Users/matt/projects/music-cross-linker/app/[...url]/page.tsx
- /Users/matt/projects/music-cross-linker/app/lib/odesli.ts

---

## Assistant

The URL normalization and Apple Music fallback logic have been updated.

1.  **Normalization Fix**: In `app/[...url]/page.tsx`, the URL handling now correctly strips mangled protocols (e.g., `https:/music.apple.com`) before prepending the correct `https://` protocol.
2.  **Robust Fallback**: The Apple Music fallback in `app/lib/odesli.ts` now uses `URL` parsing to reliably extract the track/album ID, improving robustness against varying URL structures and ensuring cleaner API calls to the iTunes lookup service.

You can verify the changes via these links:
- [/Users/matt/projects/music-cross-linker/app/[...url]/page.tsx](file:///Users/matt/projects/music-cross-linker/app/%5B...url%5D/page.tsx)
- [/Users/matt/projects/music-cross-linker/app/lib/odesli.ts](file:///Users/matt/projects/music-cross-linker/app/lib/odesli.ts)

---
