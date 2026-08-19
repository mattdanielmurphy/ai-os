---
title: "Implement YouTube Search Functionality"
date: "2026-08-13"
conversation_id: "115a94d5-5429-480c-9c23-4b92e175dbe0"
source: "antigravity"
---

# Implement YouTube Search Functionality

## User

Implement the search feature in `app/lib/youtube.ts`, create `app/api/search-youtube/route.ts`, and update `app/page.tsx` and `app/globals.css`.

1. **`app/lib/youtube.ts`**:
   - Update `YouTubeVideoCandidate` interface to include `channel?: string; thumbnail?: string;`.
   - Add `searchYouTubeVideos(query: string, limit = 10): Promise<YouTubeVideoCandidate[]>` helper function that parses `https://www.youtube.com/results?search_query=...` for up to 10 video items, extracting `id`, `title`, `channel`, and `thumbnail` (e.g., `https://i.ytimg.com/vi/${id}/hqdefault.jpg`).

2. **`app/api/search-youtube/route.ts`**:
   - Create GET route handler accepting `q` query parameter.
   - Return `{ results: candidates }` JSON.

3. **`app/page.tsx`**:
   - Revert tab interface to a single clean search input card.
   - If user input is a URL (starts with `http://`, `https://`, or contains `youtube.com`, `spotify.com`, `apple.com`, `youtu.be`), navigate directly to `/<encodeURIComponent(url)>`.
   - If user input is a text query (e.g., `artist song` or `daft punk`), fetch `/api/search-youtube?q=...` and display the 10 YouTube video search results directly under the search bar as selectable cards.
   - Clicking a card navigates to `/https://www.youtube.com/watch?v=${videoId}`.

4. **`app/globals.css`**:
   - Add styles for the search results candidate grid, video thumbnails, candidate titles, and loading state.

Execute these updates now.

---

## Assistant

The search feature has been fully implemented and integrated.

- **`app/lib/

---
