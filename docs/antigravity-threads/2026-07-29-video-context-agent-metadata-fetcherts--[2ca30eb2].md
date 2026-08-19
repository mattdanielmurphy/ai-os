---
title: "Video-context-agent: metadata-fetcher.ts"
date: "2026-07-29"
conversation_id: "2ca30eb2-b5c6-4c99-834b-b5a3ca2fa510"
source: "antigravity"
---

# Video-context-agent: metadata-fetcher.ts

## User

Modify `/Users/matt/projects/video-context-agent/src/metadata-fetcher.ts` using `replace_file_content` or `multi_replace_file_content` to add a Wikipedia synopsis fallback.

1. Add a new private method to the `MetadataFetcher` class:
```typescript
  private async fetchWikipediaSynopsis(showName: string, episodeTitle: string): Promise<string | null> {
    try {
      const searchUrl = \`https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=\${encodeURIComponent(showName + ' ' + episodeTitle)}&utf8=&format=json&origin=*\`;
      const searchRes = await fetch(searchUrl);
      if (!searchRes.ok) return null;
      const searchData = await searchRes.json();
      const results = searchData.query?.search || [];
      if (results.length === 0) return null;

      const pageTitle = results[0].title;

      const contentUrl = \`https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=&titles=\${encodeURIComponent(pageTitle)}&format=json&origin=*\`;
      const contentRes = await fetch(contentUrl);
      if (!contentRes.ok) return null;
      const contentData = await contentRes.json();

      const pages = contentData.query?.pages || {};
      const pageId = Object.keys(pages)[0];
      if (pageId === '-1') return null;

      const extract = pages[pageId].extract || '';
      if (!extract) return null;

      const plotMatch = extract.match(/==\\s*(Plot|Synopsis)\\s*==\\n([\\s\\S]*?)(?=\\n==|$)/i);
      if (plotMatch && plotMatch[2].trim()) {
        return plotMatch[2].trim();
      }

      const paragraphs = extract.split('\\n\\n');
      if (paragraphs.length > 0 && paragraphs[0].trim()) {
        return paragraphs[0].trim();
      }
    } catch (e) {
      console.error("Wikipedia fetch failed", e);
    }
    return null;
  }
```

2. Modify the fallback logic inside `fetchMetadata` (lines 58-65) to:
```typescript
      let overview = epData.overview || '';
      // Fallback 1: Wikipedia Plot/Synopsis
      if (overview.length < 150) {
        const wikiOverview = await this.fetchWikipediaSynopsis(showName, epData.name || '');
        if (wikiOverview && wikiOverview.length >= 150) {
          overview = wikiOverview;
        }
      }
      // Fallback 2: TVmaze
      if (overview.length < 150) {
        const tvmazeOverview = await this.fetchTVMazeSynopsis(showName, season, episode);
        if (tvmazeOverview) {
          overview = tvmazeOverview;
        }
      }
```

---

## Assistant

Created At: 2026-07-28T23:44:43-06:00
Completed At: 2026-07-28T23:44:43-06:00
File Path: `file:///Users/matt/projects/video-context-agent/src/metadata-fetcher.ts`
Total Lines: 97
Total Bytes: 3251
Showing lines 1 to 97
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: export interface CastMember {
2:   character: string;
3:   name: string;
4: }
5: 
6: export interface EpisodeMetadata {
7:   name: string;
8:   overview: string;
9:   cast: CastMember[];
10: }
11: 
12: export class MetadataFetcher {
13:   private apiKey: string | undefined;
14: 
15:   constructor() {
16:     this.apiKey = process.env.TMDB_API_KEY;
17:   }
18: 
19:   public parseFilename(filename: string): { showName: string, season: number, episode: number } | null {
20:     const regex = /(.+?)[.\s_-]+[sS](\d{1,2})[eE](\d{1,2})/;
21:     const match = filename.match(regex);
22:     if (match) {
23:       return {
24:         showName: match[1].replace(/[.\s_-]+/g, ' ').trim(),
25:         season: parseInt(match[2], 10),
26:         episode: parseInt(match[3], 10)
27:       };
28:     }
29:     return null;
30:   }
31: 
32:   public async fetchMetadata(showName: string, season: number, episode: number): Promise<EpisodeMetadata | null> {
33:     if (!this.apiKey) {
34:       console.warn("No TMDB_API_KEY found in environment.");
35:       return null;
36:     }
37:     try {
38:       const searchUrl = new URL('https://api.themoviedb.org/3/search/tv');
39:       searchUrl.searchParams.append('query', showName);
40:       searchUrl.searchParams.append('api_key', this.apiKey);
41: 
42:       const searchRes = await fetch(searchUrl.toString());
43:       const searchData = await searchRes.json();
44: 
45:       if (!searchData.results || searchData.results.length === 0) return null;
46:       const showId = searchData.results[0].id;
47: 
48:       const epUrl = 
<truncated 78 bytes>
?api_key=${this.apiKey}&append_to_response=credits`;
49:       const epRes = await fetch(epUrl);
50:       const epData = await epRes.json();
51: 
52:       if (!epData || !epData.credits) return null;
53: 
54:       const allCast: CastMember[] = [];
55:       if (epData.credits.cast) allCast.push(...epData.credits.cast.map((c: any) => ({ character: c.character, name: c.name })));
56:       if (epData.credits.guest_stars) allCast.push(...epData.credits.guest_stars.map((c: any) => ({ character: c.character, name: c.name })));
57: 
58:       let overview = epData.overview || '';
59:       // If the TMDB overview is missing or very brief (< 150 characters), try TVmaze as a fallback
60:       if (overview.length < 150) {
61:         const tvmazeOverview = await this.fetchTVMazeSynopsis(showName, season, episode);
62:         if (tvmazeOverview) {
63:           overview = tvmazeOverview;
64:         }
65:       }
66: 
67:       return {
68:         name: epData.name || '',
69:         overview: overview,
70:         cast: allCast
71:       };
72:     } catch (e) {
73:       console.error("Failed to fetch metadata from TMDB", e);
74:       return null;
75:     }
76:   }
77: 
78:   private async fetchTVMazeSynopsis(showName: string, season: number, episode: number): Promise<string | null> {
79:     try {
80:       const url = `https://api.tvmaze.com/singlesearch/shows?q=${encodeURIComponent(showName)}&embed=episodes`;
81:       const res = await fetch(url);
82:       if (!res.ok) return null;
83:       const data = await res.json();
84:       const episodes = data._embedded?.episodes || [];
85:       const ep = episodes.find((e: any) => e.season === season && e.number === episode);
86:       if (ep && ep.summary) {
87:         // Strip HTML tags
88:         return ep.summary.replace(/<[^>]*>?/gm, '');
89:       }
90:     } catch (e) {
91:       console.error("TVmaze fetch failed", e);
92:     }
93:     return null;
94:   }
95: }
96: 
97: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-07-28T23:44:46-06:00
Completed At: 2026-07-28T23:44:46-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/video-context-agent/src/metadata-fetcher.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -56,7 +56,14 @@
       if (epData.credits.guest_stars) allCast.push(...epData.credits.guest_stars.map((c: any) => ({ character: c.character, name: c.name })));
 
       let overview = epData.overview || '';
-      // If the TMDB overview is missing or very brief (< 150 characters), try TVmaze as a fallback
+      // Fallback 1: Wikipedia Plot/Synopsis
+      if (overview.length < 150) {
+        const wikiOverview = await this.fetchWikipediaSynopsis(showName, epData.name || '');
+        if (wikiOverview && wikiOverview.length >= 150) {
+          overview = wikiOverview;
+        }
+      }
+      // Fallback 2: TVmaze
       if (overview.length < 150) {
         const tvmazeOverview = await this.fetchTVMazeSynopsis(showName, season, episode);
         if (tvmazeOverview) {
@@ -74,6 +74,44 @@
     }
   }
 
+  private async fetchWikipediaSynopsis(showName: string, episodeTitle: string): Promise<string | null> {
+    try {
+      const searchUrl = `https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(showName + ' ' + episodeTitle)}&utf8=&format=json&origin=*`;
+      const searchRes = await fetch(searchUrl);
+      if (!searchRes.ok) return null;
+      const searchData = await searchRes.json();
+      const results = searchData.query?.search || [];
+      if (results.length === 0) return null;
+
+      const pageTitle = results[0].title;
+
+      const contentUrl = `https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=&titles=${encodeURIComponent(pageTitle)}&format=json&origin=*`;
+      const contentRes = await fetch(contentUrl);
+      if (!contentRes.ok) return null;
+      const contentData = await contentRes.json();
+
+      const pages = contentData.query?.pages || {};
+      const pageId = Object.keys(pages)[0];
+      if (pageId === '-1') return null;
+
+      const extract = pages[pageId].extract || '';
+      if (!extract) return null;
+
+      const plotMatch = extract.match(/==\s*(Plot|Synopsis)\s*==\n([\s\S]*?)(?=\n==|$)/i);
+      if (plotMatch && plotMatch[2].trim()) {
+        return plotMatch[2].trim();
+      }
+
+      const paragraphs = extract.split('\n\n');
+      if (paragraphs.length > 0 && paragraphs[0].trim()) {
+        return paragraphs[0].trim();
+      }
+    } catch (e) {
+      console.error("Wikipedia fetch failed", e);
+    }
+    return null;
+  }
+
   private async fetchTVMazeSynopsis(showName: string, season: number, episode: number): Promise<string | null> {
     try {
       const url = `https://api.tvmaze.com/singlesearch/shows?q=${encodeURIComponent(showName)}&embed=episodes`;
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-07-28T23:44:47-06:00
Completed At: 2026-07-28T23:44:47-06:00
Message sent to "ee00be31-7ce0-4f8b-93e9-27f5aee8e25b".

Created At: 2026-07-28T23:44:48-06:00
Completed At: 2026-07-28T23:44:49-06:00
Message sent to "ee00be31-7ce0-4f8b-93e9-27f5aee8e25b".

The requested changes have been applied to `/Users/matt/projects/video-context-agent/src/metadata-fetcher.ts`. The new `fetchWikipediaSynopsis` method has been added, and the `fetchMetadata` method now includes the updated fallback logic to check Wikipedia before resorting to TVmaze for short overviews. I have notified the parent agent.

---
