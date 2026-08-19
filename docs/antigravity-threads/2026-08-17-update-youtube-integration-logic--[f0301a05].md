---
title: "Update YouTube Integration Logic"
date: "2026-08-17"
conversation_id: "f0301a05-12a5-4546-8e50-d08271f79030"
source: "antigravity"
---

# Update YouTube Integration Logic

## User

Please apply the following exact code updates:

1. In `app/lib/youtube.ts`:
Replace `searchYouTubeVideos` and `getTopVideos` with:
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

  try {
    const ytInitialDataMatch = html.match(/var ytInitialData = ({.*?});<\/script>/);
    if (ytInitialDataMatch) {
      const ytInitialData = JSON.parse(ytInitialDataMatch[1]);
      const contents =
        ytInitialData.contents?.twoColumnSearchResultsRenderer?.primaryContents?.sectionListRenderer?.contents || [];

      for (const section of contents) {
        const itemSection = section.itemSectionRenderer?.contents || [];
        for (const item of itemSection) {
          const video = item.videoRenderer;
          if (video && video.videoId) {
            const titleRuns = video.title?.runs?.map((r: any) => r.text).join('') || video.title?.simpleText || 'YouTube Video';
            const channel = video.ownerText?.runs?.map((r: any) => r.text).join('') || video.shortBylineText?.runs?.map((r: any) => r.text).join('') || video.longBylineText?.runs?.map((r: any) => r.text).join('');
            candidates.push({
              id: video.videoId,
              title: titleRuns,
              channel: channel || undefined,
              thumbnail: video.thumbnail?.thumbnails?.[0]?.url || `https://i.ytimg.com/vi/${video.videoId}/hqdefault.jpg`,
            });
          }
          if (candidates.length >= limit) break;
        }
        if (candidates.length >= limit) break;
      }
    }
  } catch (e) {
    console.error('Failed to parse ytInitial
<truncated 4649 bytes>
ates}
          entityId={entityId}
          currentUrl={currentUrl}
          initialQuery={searchTerm}
          onUpdateMatch={handleUpdateMatch}
        />
      )}
    </>
  );
}
```

4. In `app/components/track-view/YouTubeSection.tsx`:
Replace with:
```tsx
import { resolveYoutubePlatform, EntityContext } from '../../lib/urlResolver';
import { getTopVideos } from '../../lib/youtube';
import YouTubePlayer from './YouTubePlayer';

export default async function YouTubeSection({
  ctx,
  artist,
  title,
  explicitVideoId,
  sourceUrl,
}: {
  ctx: EntityContext;
  artist: string;
  title: string;
  explicitVideoId?: string;
  sourceUrl?: string;
}) {
  const isExplicitSource = !!sourceUrl?.includes('youtube.com') || !!sourceUrl?.includes('youtu.be');

  if (explicitVideoId) {
    return (
      <div className="player-wrapper">
        <iframe
          src={`https://www.youtube.com/embed/${explicitVideoId}?autoplay=0`}
          title={`${title} by ${artist}`}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          suppressHydrationWarning={true}
        />
      </div>
    );
  }

  let videoId = '';
  const crossLink = await resolveYoutubePlatform(ctx, sourceUrl);
  if (crossLink?.url) {
    videoId = crossLink.url.match(/(?:v=|youtu\.be\/|embed\/)([\w-]{11})/)?.[1] || '';
  }

  if (!videoId) {
    const videos = await getTopVideos(artist || title, title, ctx.isAlbum ? 'album' : 'track', 5);
    videoId = videos[0]?.id || '';
  }

  if (!videoId) return null;

  return (
    <YouTubePlayer
      initialVideoId={videoId}
      artist={artist}
      title={title}
      entityId={ctx.entityId}
      isExplicitSource={isExplicitSource}
      candidates={crossLink?.candidates || []}
      currentUrl={crossLink?.url || `https://www.youtube.com/watch?v=${videoId}`}
      searchTerm={ctx.searchTerm}
    />
  );
}
```

---

## Assistant

The requested updates have been successfully applied to the following files:

*   [`app/lib/youtube.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/youtube.ts): Updated `searchYouTubeVideos` and `getTopVideos` for more robust searching.
*   [`app/lib/urlResolver.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts): Updated `classifyMatch` with improved matching logic.
*   [`app/components/track-view/YouTubePlayer.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/track-view/YouTubePlayer.tsx): Updated component for handling state updates of YouTube video IDs and URLs.
*   [`app/components/track-view/YouTubeSection.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/track-view/YouTubeSection.tsx): Updated to incorporate the new YouTube search functionality and handle missing video IDs.

I have notified the parent agent.

---
