---
title: "Update Youtube Title Parser"
date: "2026-08-13"
conversation_id: "9d26a775-8915-4c92-8fa7-b9436970f3b9"
source: "antigravity"
---

# Update Youtube Title Parser

## User

Please update `app/lib/youtube/titleParser.ts` and `app/lib/youtube/titleParser.test.ts`.

1. In `app/lib/youtube/titleParser.ts`:
   In `stripNoiseTags(text: string)`, update the noise regex patterns to strip out "full album" (and "full album stream", "full album audio", etc.) regardless of whether it is wrapped in parens/brackets or appearing as standalone text.
   Specifically:
   - Add standalone noise pattern replacements for `/\\b(full album|full album stream|full album audio|full album playlist)\\b/gi` as well as any trailing/leading noise.
   - Also ensure `/\\((seamless transitions|seamless transition)\\)/gi` or `/\\b(seamless transitions|seamless transition)\\b/gi` or generic noise phrases commonly found in YT titles like "full album" without brackets are stripped cleanly.
   - Ensure cleanYouTubeTitle trims whitespace and handles cleaned empty parens/brackets gracefully.

2. In `app/lib/youtube/titleParser.test.ts`:
   Add test cases verifying that:
   - 'Ravedeath 1972 (Seamless transitions) Full album' cleans to 'Ravedeath 1972'
   - 'Tim Hecker - Ravedeath 1972 (Seamless transitions) Full album' parses to artist: 'Tim Hecker', title: 'Ravedeath 1972'
   - Unparenthesized 'Full album' at the end of titles is cleanly removed.

Target files:
- `/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts`
- `/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.test.ts`

---

## Assistant

The updates to `app/lib/youtube/titleParser.ts` and `app/lib/youtube/titleParser.test.ts` have been completed successfully.

- **`app/lib/youtube/titleParser.ts`**: Updated `stripNoiseTags` to include more comprehensive regex patterns for "full album" (including stream/audio/playlist variants) and "seamless transitions", both within brackets/parentheses and as standalone text.
- **`app/lib/youtube/titleParser.test.ts`**: Added test cases to verify cleaning of "Seamless transitions" and "Full album" in various contexts.

---
