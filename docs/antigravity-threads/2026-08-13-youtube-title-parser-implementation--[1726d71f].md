---
title: "YouTube Title Parser Implementation"
date: "2026-08-13"
conversation_id: "1726d71f-61fb-4e6b-b801-b0744ad90651"
source: "antigravity"
---

# YouTube Title Parser Implementation

## User

Create the file `/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts` and `/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.test.ts` to implement the hybrid YouTube title cleaning and parsing pipeline.

### Requirements for `app/lib/youtube/titleParser.ts`:
1. `decodeHtmlEntities(text: string): string` - decodes HTML entities (`&amp;`, `&#39;`, `&quot;`, `&lt;`, `&gt;`, `&nbsp;`).
2. `normalizeBrackets(text: string): string` - replaces full-width/CJK brackets `（）`, `【】`, `［］` with standard ASCII `()`, `[]`.
3. `stripNoiseTags(text: string): string` - strips noise tags (case-insensitive, recursive loop until no more matches):
   - Tags like `(Official Video)`, `(Official Music Video)`, `(Official Audio)`, `(Official Lyric Video)`, `(Lyric Video)`, `(Official HD Video)`, `(Visualizer)`, `(Full Album)`, `(Full Album Stream)`, `(HQ)`, `(HD)`, `(4K)`, `(1080p)`, `(Lyrics)`, `(Audio)`, `(Explicit)`, `(Clean)`, `(Deluxe Edition)`, `(Remastered ...)`, `(\d{4} Remaster)`
   - Note: Do NOT strip general parens like `(Demo)` or `(Live Aid)` - only explicit allowlist patterns!
4. `repairUnmatchedBrackets(text: string): string` - depth-aware bracket counter. If an opening `(` or `[` is left unmatched at the end (or anywhere), or if there are dangling closing brackets `)` or `]`, repairs/strips them safely without cutting off valid content.
5. `cleanYouTubeTitle(raw: string): string` - composes: decodeHtmlEntities -> normalizeBrackets -> stripNoiseTags -> repairUnmatchedBrackets -> clean extra whitespace and trailing/leading separator punctuation (`-`, `|`, `:`, `,`).
6. `parseYouTubeTitle(rawTitle: string, channelName?: string): { artist: string | null; title: string }`
   - First cleans the raw title via `cleanYouTubeTitle`.
   - Checks `channelName`: if channel ends with ` - Topic` (e.g. `Queen - Topic`), strip ` - Topic` and use `Queen` as artist signal if title lacks one.
   - Splits on spaced hyphens ` - `, ` – `, ` — ` (require whitespace around hyphen
<truncated 56 bytes>
tist "Title"` or `Artist “Title”`.
   - Cleans leading/trailing quotes/whitespace from artist & title.
7. `getChromeAIAvailability(): Promise<'available' | 'unavailable'>`
   - Feature detect `LanguageModel.availability()` (or legacy `self.ai.languageModel.capabilities()`). Returns `'available'` only if ready without download.
8. `parseYouTubeTitleHybrid(rawTitle: string, channelName?: string): Promise<{ artist: string | null; title: string }>`
   - Calls `cleanYouTubeTitle(rawTitle)`.
   - If in browser environment (`typeof window !== 'undefined'`) and `getChromeAIAvailability()` is `'available'`, attempts `window.ai` / `LanguageModel` with AbortController 1.5s timeout and `responseConstraint` schema `{ type: 'object', properties: { artist: { type: 'string' }, title: { type: 'string' } }, required: ['title'] }`. Destroys session in `finally`.
   - If AI fails/unavailable/times out, returns `parseYouTubeTitle(rawTitle, channelName)`.

### Requirements for `app/lib/youtube/titleParser.test.ts`:
Create a comprehensive test suite testing Bun test (`import { describe, it, expect } from 'bun:test'`):
- HTML entity decoding (`Led Zeppelin &amp; Friends` -> `Led Zeppelin & Friends`).
- Noise tag stripping (`Led Zeppelin - Physical Graffiti (Full Album) [Official Video]` -> `Led Zeppelin - Physical Graffiti`).
- Unmatched paren repair (`Led Zeppelin - Physical Graffiti (` -> `Led Zeppelin - Physical Graffiti`).
- Spaced hyphen artist/title split (`Led Zeppelin - Physical Graffiti` -> artist: `Led Zeppelin`, title: `Physical Graffiti`).
- Hyphenated artist name preserved (`AC-DC - Highway to Hell` -> artist: `AC-DC`, title: `Highway to Hell`).
- CJK bracket normalization (`【Official Video】 Pink Floyd - Time` -> artist: `Pink Floyd`, title: `Time`).
- Topic channel parsing (`Physical Graffiti`, channel `Led Zeppelin - Topic` -> artist: `Led Zeppelin`, title: `Physical Graffiti`).

Write both files now.

---

## Assistant

The `titleParser.ts` and `titleParser.test.ts` files have been created in `/Users/matt/projects/music-cross-linker/app/lib/youtube/`.

- [`titleParser.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts) implements the requested YouTube title cleaning, bracket handling, noise tag stripping, and hybrid parsing logic.
- [`titleParser.test.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.test.ts) provides a Bun test suite covering HTML decoding, noise stripping, bracket repairs, artist/title splitting, CJK normalization, and channel-based metadata extraction.

---
