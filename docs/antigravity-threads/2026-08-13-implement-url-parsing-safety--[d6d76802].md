---
title: "Implement URL Parsing Safety"
date: "2026-08-13"
conversation_id: "d6d76802-5ed1-4e26-b32e-fc069dbefc31"
source: "antigravity"
---

# Implement URL Parsing Safety

## User

In /Users/matt/projects/music-cross-linker/app/[...url]/page.tsx, wrap the DB entity resolution and searchParams handling safely so 500 server errors on invalid or external URLs are caught gracefully or handled properly.

Specifically, check app/[...url]/page.tsx:
When `rawJoined` or `urlSegments` contains double slashes or protocol strings like `https:` or `https:/`, or when `isExternalUrl` is true:
Ensure `decodeURIComponent` does not crash if given invalid percent-encoding, and ensure missing DB env vars or DB query failures in `TrackView` (or `resolveEntity`) fallback to rendering `ResolvingRedirect` or graceful fallback rather than throwing a 500 Error.

In `app/[...url]/page.tsx`:
Add safety checks around `decodeURIComponent`:
```ts
function safeDecode(str: string): string {
  try {
    return decodeURIComponent(str);
  } catch {
    return str;
  }
}
```
Use `safeDecode(rawJoined)` instead of `decodeURIComponent(rawJoined)`.

Also, for external URLs, normalize single-slash `https:/` or `http:/` to `https://`:
```ts
let cleaned = safeDecode(rawJoined).replace(/^(https?:\/*)+/i, 'https://');
```

And in `app/components/track-view/TrackView.tsx`, ensure any error inside `resolveEntity` or header/geo detection doesn't crash the server component with 500:
`ctx` is already caught in a try/catch, but ensure `getPaletteFromImage` or other operations also never throw uncaught exceptions.

Apply the `safeDecode` fix to `/Users/matt/projects/music-cross-linker/app/[...url]/page.tsx`.

---
