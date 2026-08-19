---
title: "Update Candidate List UI"
date: "2026-08-12"
conversation_id: "884ff3b5-e442-4b02-aaf3-36cba89141f1"
source: "antigravity"
---

# Update Candidate List UI

## User

Update `PlatformButton.tsx` and `CandidateList.tsx` for "See Search Results" mode when no confident match exists.

In `app/components/track-view/PlatformButton.tsx`:
1. Remove the `!isNoMatch(active)` condition wrapping `<CandidateList ... />` on line 87 so CandidateList is rendered even when `isNoMatch(active)` is true.
2. Pass `isNoMatch={isNoMatch(active)}` to `CandidateList`.

In `app/components/track-view/CandidateList.tsx`:
1. Accept `isNoMatch` prop in `CandidateList({ platform, candidates, entityId, currentUrl, initialQuery, onUpdateMatch, isNoMatch }: any)`.
2. Update toggle button text (line 93):
   - If `isOpen`: `'Close'`
   - Else if `isNoMatch`: `'See search results'`
   - Else: `'Not Right?'`
3. Add a `useEffect` hook or trigger inside `setIsOpen`: when `isOpen` becomes `true` and `isNoMatch` is true, if `!searched` and `initialQuery`, automatically call `runSearch()` so search results populate immediately when opened.
4. Filter candidate cards display: filter out items where `typeof c.source === 'string' && c.source.endsWith('_fallback')` so dummy fallback entries are hidden from candidate list cards.

Target files:
- /Users/matt/projects/music-cross-linker/app/components/track-view/PlatformButton.tsx
- /Users/matt/projects/music-cross-linker/app/components/track-view/CandidateList.tsx

---

## Assistant

I have successfully updated `PlatformButton.tsx` and `CandidateList.tsx`.

*   **[`PlatformButton.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/track-view/PlatformButton.tsx)**: Now renders `CandidateList` even when no match is found, passing the `isNoMatch` status.
*   **[`CandidateList.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/track-view/CandidateList.tsx)**:
    *   Updated the toggle button label to show **'See search results'** when no match exists.
    *   Added a `useEffect` hook to automatically perform a search when opened if no match exists and an initial query is present.
    *   Added logic to filter out placeholder 'fallback' candidate cards.

I have notified the parent agent of these changes.

---
