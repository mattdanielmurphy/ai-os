---
title: "Update TrackView Slug Formatting"
date: "2026-08-12"
conversation_id: "30dc5049-423a-4b00-b72b-5d92feb74ca9"
source: "antigravity"
---

# Update TrackView Slug Formatting

## User

Update `formatSlug` in `app/components/track-view/TrackView.tsx`:
Currently, line 61-65:
```ts
  const formatSlug = (slug: string) =>
    decodeURIComponent(slug)
      .split('-')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
```
Change `formatSlug` so that it preserves numeric ranges like `85-92` or `1985-1992` instead of splitting them with spaces.
For example, `split(/-(?!\d+)/)` or checking if adjacent tokens are numbers so that `selected-ambient-works-85-92` formats as `Selected Ambient Works 85-92` rather than `Selected Ambient Works 85 92`.

Target file: /Users/matt/projects/music-cross-linker/app/components/track-view/TrackView.tsx

---

## Assistant

The `formatSlug` function in `app/components/track-view/TrackView.tsx` has been updated to preserve numeric ranges. Instead of splitting every hyphen, it now uses a regex split `/(?<!\d)-(?!\d)/` which ensures hyphens surrounded by digits are not treated as separators.

**Changes applied:**
[TrackView.tsx](file:///Users/matt/projects/music-cross-linker/app/components/track-view/TrackView.tsx)

```diff
-      .split('-')
+      .split(/(?<!\d)-(?!\d)/)
```

---
