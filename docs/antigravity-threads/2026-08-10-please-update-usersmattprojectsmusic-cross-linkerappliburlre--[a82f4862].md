---
title: "Please update `/Users/matt/projects/music-cross-linker/app/lib/urlReso"
date: "2026-08-10"
conversation_id: "a82f4862-b8d0-403c-8f40-44d82a3e7c04"
source: "antigravity"
---

# Please update `/Users/matt/projects/music-cross-linker/app/lib/urlReso

## User

Please update `/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts` and `/Users/matt/projects/music-cross-linker/app/[artist]/[track]/page.tsx` in `/Users/matt/projects/music-cross-linker`:

1. Update `app/lib/urlResolver.ts`:
- Fix iTunes Search API query:
  Add `&media=music&entity=album` or `&media=music&entity=song` to the iTunes search query:
  `https://itunes.apple.com/search?term=${encodeURIComponent(artist + ' ' + title)}&media=music&country=${countryCode.toLowerCase()}&limit=5`
  Filter `itunesSearch.results` to ensure `result.kind === 'song'` or `result.wrapperType === 'collection'` or `result.collectionViewUrl?.includes('music.apple.com')` or `result.trackViewUrl?.includes('music.apple.com')`.
  Never match podcasts or audiobooks (`podcasts.apple.com`).

2. Update `app/[artist]/[track]/page.tsx`:
- Format artist and track slugs properly (capitalized, spaces restored):
  ```typescript
  const formatSlug = (slug: string) =>
    decodeURIComponent(slug)
      .split('-')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  const a = formatSlug(artist);
  const t = formatSlug(track);
  ```
- On the `<iframe>` element, add `suppressHydrationWarning={true}` to prevent client/server hydration warnings.

---

## Assistant

Finished updating the requested files.

---
