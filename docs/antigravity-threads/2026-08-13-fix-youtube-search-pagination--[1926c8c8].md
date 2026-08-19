---
title: "Fix YouTube Search Pagination"
date: "2026-08-13"
conversation_id: "1926c8c8-2f27-4f08-a041-a821cead7e26"
source: "antigravity"
---

# Fix YouTube Search Pagination

## User

Fix CandidateList.tsx and youtube.ts so YouTube "Load More Results" doesn't clear or get stuck:

1. Update `app/lib/youtube.ts`:
Refine `searchYouTubeVideos` parsing:
Instead of a single brittle regex matching `videoRenderer` blocks across the HTML, extract video IDs, titles, channels, and thumbnails robustly:
```ts
export async function searchYouTubeVideos(
  query: string,
  limit = 10
): Promise<YouTubeVideoCandidate[]> {
  const encodedQuery = encodeURIComponent(query);
  const res = await fetch(`https://www.youtube.com/results?search_query=${encodedQuery}`, {
    headers: {
      'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    },
  });
  const html = await res.text();

  const candidates: YouTubeVideoCandidate[] = [];
  const seenIds = new Set<string>();

  // Extract all videoRenderer JSON blocks or videoId matches
  const videoIdMatches = Array.from(html.matchAll(/"videoId"\s*:\s*"([a-zA-Z0-9_-]{11})"/g));

  for (const match of videoIdMatches) {
    const id = match[1];
    if (seenIds.has(id)) continue;

    // Find the slice of HTML around this videoId to get title and channel name
    const idx = match.index || 0;
    const block = html.slice(idx, idx + 2500);

    const titleMatch = block.match(/"title"\s*:\s*\{\s*"runs"\s*:\s*\[\s*\{\s*"text"\s*:\s*"(.*?)"/);
    const channelMatch = block.match(/"longBylineText":[\s\S]*?"text":"(.*?)"/);

    const videoTitle = titleMatch ? titleMatch[1].replace(/\\"/g, '"').replace(/\\u0026/g, '&') : 'YouTube Video';
    const channel = channelMatch ? channelMatch[1] : undefined;
    const thumbnail = `https://i.ytimg.com/vi/${id}/hqdefault.jpg`;

    seenIds.add(id);
    candidates.push({ id, title: videoTitle, channel, thumbnail });

    if (candidates.length >= limit) break;
  }

  return candidates;
}
```

2. Update `app/components/track-view/CandidateList.tsx`:
In `runSearch`:
When `searched` is set to `true` and new results are returned, ensure that if `data.candidates` is returned as empty or fails, `results` isn't wiped out unless intended, or preserve existing results if `newResults.length > 0`:
```ts
      const res = await fetch(`/api/entities/${entityId}/search?platform=${platform}&query=${encodeURIComponent(trimmed)}&limit=${currentLimit}`);
      const data = await res.json();
      if (data.candidates && data.candidates.length > 0) {
        setResults(data.candidates);
      }
      setSearched(true);
```

Apply these edits carefully to both files.

---

## Assistant

The requested updates have been applied:

1.  **`app/lib/youtube.ts`**: The `searchYouTubeVideos` function now uses a more robust regex-based extraction method to find video IDs, titles, and channel information from the YouTube results page, improving reliability.
2.  **`app/components/track-view/CandidateList.tsx`**: The `runSearch` function was updated to check for new candidates in the API response before updating the state. This ensures that the results list is not inadvertently wiped out when loading more results.

---
