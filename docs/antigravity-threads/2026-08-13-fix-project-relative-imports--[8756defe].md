---
title: "Fix Project Relative Imports"
date: "2026-08-13"
conversation_id: "8756defe-cfc7-4c22-9564-105bce7f5b3a"
source: "antigravity"
---

# Fix Project Relative Imports

## User

Fix relative imports in `app/api/search-youtube/route.ts` and `app/page.tsx`:

In `app/api/search-youtube/route.ts`:
Change `import { searchYouTubeVideos } from '@/lib/youtube';` to `import { searchYouTubeVideos } from '../../lib/youtube';`

In `app/page.tsx`:
Change `import { YouTubeVideoCandidate } from "@/lib/youtube";` to `import { YouTubeVideoCandidate } from "./lib/youtube";`

Execute these fixes now.

---

## Assistant

The relative imports in `app/api/search-youtube/route.ts` and `app/page.tsx` have been updated as requested.

---
