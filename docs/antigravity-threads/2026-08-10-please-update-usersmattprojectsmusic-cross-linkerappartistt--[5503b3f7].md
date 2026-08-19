---
title: "Please update `/Users/matt/projects/music-cross-linker/app/[artist]/[t"
date: "2026-08-10"
conversation_id: "5503b3f7-5431-477b-861f-7d5fab2b7e3c"
source: "antigravity"
---

# Please update `/Users/matt/projects/music-cross-linker/app/[artist]/[t

## User

Please update `/Users/matt/projects/music-cross-linker/app/[artist]/[track]/page.tsx`, `/Users/matt/projects/music-cross-linker/app/components/LinkButtons.tsx`, and `/Users/matt/projects/music-cross-linker/app/globals.css` in `/Users/matt/projects/music-cross-linker`:

1. Update `app/[artist]/[track]/page.tsx`:
- Restore YouTube embed logic & fallback:
  If `youtubeUrl` contains a video ID, extract `videoId`.
  If no `videoId` from `youtubeUrl`, call `getTopVideos(a, t, isAlbum ? 'album' : 'track', 5)` to get fallback videos, setting `videoId = videos[0]?.id`.
- Render:
  - `.track-card.glass` container centered on page.
  - Header with `.badge` ('Album Link' or 'Track Link'), `.track-title` ("Belladonna"), `.track-artist` ("by Daniel Lanois").
  - Embedded YouTube iframe in `.player-wrapper`: `<iframe src="https://www.youtube.com/embed/${videoId}?autoplay=0" title="${t} by ${a}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen />` if `videoId` is present.
  - Pass `appleUrl`, `spotifyUrl`, `youtubeUrl`, `country` to `<LinkButtons />`.

2. Update `app/components/LinkButtons.tsx`:
- Simplify to ONE Region selector setting:
  Show a single sleek region banner at top (`Region: 🇨🇦 Canada ▾`).
  REMOVE the extra giant flag button from the link grid.
- Render clean, centered platform buttons for Spotify, Apple Music, and YouTube:
  Each button links directly to the platform URL.
  Show platform icon + label (e.g., Spotify, Apple Music, YouTube).
- Keep the interactive region selection modal when clicking the region banner.

3. Update `app/globals.css`:
- Remove background gradients: `body` background should be clean solid dark `#050505`.
- Center the main content, card, and buttons with generous margin and padding (`margin: 0 auto; gap: 1.75rem`).
- Ensure `.track-title` is prominent, clean white text, and `.track-artist` is nicely styled.
- Keep `.player-wrapper` (16:9 aspect ratio responsive embed) and glassmorphic card styling.
- Center `.btn-link-grid` and button text cleanly.

---

## Assistant

The requested updates have been applied to `/Users/matt/projects/music-cross-linker`.

### Summary of Changes

*   **[`page.tsx`](file:///Users/matt/projects/music-cross-linker/app/%5Bartist%5D/%5Btrack%5D/page.tsx)**:
    *   Added logic to extract `videoId` from `youtubeUrl`.
    *   Implemented fallback using `getTopVideos` if no ID is found.
    *   Updated the layout to use a centered `.track-card.glass` container with the track info and the YouTube player.
*   **[`LinkButtons.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/LinkButtons.tsx)**:
    *   Simplified UI: Removed the giant flag button from the grid.
    *   Maintained the region selector banner at the top.
    *   Cleaned up platform buttons.
*   **[`globals.css`](file:///Users/matt/projects/music-cross-linker/app/globals.css)**:
    *   Updated `body` background to a solid `#050505`.
    *   Ensured consistent centering and padding for the main layout.

---
