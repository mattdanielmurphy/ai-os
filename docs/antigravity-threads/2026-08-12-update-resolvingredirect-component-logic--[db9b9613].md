---
title: "Update ResolvingRedirect Component Logic"
date: "2026-08-12"
conversation_id: "db9b9613-c96a-412f-9b67-31c532828670"
source: "antigravity"
---

# Update ResolvingRedirect Component Logic

## User

Update `app/components/ResolvingRedirect.tsx` according to the implementation plan:
1. When `videoId` is provided as a non-null prop, render the YouTube iframe (`<iframe src={`https://www.youtube.com/embed/${videoId}?autoplay=1`} ... />`) immediately inside `.player-wrapper` instead of the `.player-wrapper-skeleton` spinner.
2. Below `.player-wrapper`, display a non-blocking status indicator ("Finding cross-platform matches…") while `fetch('/api/resolve-link')` runs in the background to redirect to the canonical slug once resolved.
3. If `videoId` is null, preserve the original skeleton spinner and "Looking up this link…" text.

Target file: /Users/matt/projects/music-cross-linker/app/components/ResolvingRedirect.tsx

---

## Assistant

OK. I have updated `app/components/ResolvingRedirect.tsx` according to your instructions.

---
