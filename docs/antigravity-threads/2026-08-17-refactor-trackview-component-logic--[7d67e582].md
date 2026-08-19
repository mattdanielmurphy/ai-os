---
title: "Refactor TrackView Component Logic"
date: "2026-08-17"
conversation_id: "7d67e582-3660-4932-bae5-1097d0892961"
source: "antigravity"
---

# Refactor TrackView Component Logic

## User

In `app/components/track-view/TrackView.tsx`:
Restore `const parsed = !a ? parseMusicTitle(displaySource) : null;` before `const displayPrimary = ...` so that `parsed` and `displaySource` are defined.

Specifically:
```tsx
  const displaySource = t;
  const parsed = !a ? parseMusicTitle(displaySource) : null;
  const displayPrimary = ctx.canonicalTitle || (parsed ? parsed.primary : displaySource);
  const displaySecondary = ctx.canonicalArtist || (parsed ? parsed.secondary : (a || null));
  const displayYear = parsed?.year || null;
```

Also check `TypeBadge.tsx` import: since TrackView is a server component, `import TypeBadge from './TypeBadge'` can be a regular top-level import.

---

## Assistant

The requested changes to `app/components/track-view/TrackView.tsx` have been completed:

*   The `displaySource` and `parsed` variables have been restored to the component body.
*   `TypeBadge` has been moved to a top-level import, and the dynamic `await import` has been removed.

[TrackView.tsx](file:///Users/matt/projects/music-cross-linker/app/components/track-view/TrackView.tsx)

---
