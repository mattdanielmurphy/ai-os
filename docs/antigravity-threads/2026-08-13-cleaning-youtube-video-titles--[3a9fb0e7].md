---
title: "Cleaning YouTube Video Titles"
date: "2026-08-13"
conversation_id: "3a9fb0e7-7ade-4fbb-bda2-5211be5b6e6b"
source: "antigravity"
---

# Cleaning YouTube Video Titles

## User

We have to handle the case, which is pretty common for YouTube, albums, etc. Where there's open parenthesis, full album, close parenthesis, at the end of the video title.
In fact, we should be doing a robust clean up of the video title
I recently learned that we can actually take advantage of the tiny local model that ships by default with Chrome. Do you think that would be good at doing a clean, intelligent parsing of the YouTube video title to actually identify the artist and title, etc.?
/planner

---

## Assistant

I have evaluated Chrome's built-in local AI model (`window.ai` / Prompt API) vs a deterministic parsing pipeline, and prepared a detailed implementation plan in [implementation_plan.md](file:///Users/matt/.gemini/antigravity/brain/3a9fb0e7-7ade-4fbb-bda2-5211be5b6e6b/implementation_plan.md).

### Key Takeaways & Evaluation
1. **Chrome Built-in AI (`window.ai` / Gemini Nano) Evaluation:**
   - **Recommendation:** Do not use `window.ai` for YouTube title cleaning.
   - **Why:** `window.ai` is client browser-only (unavailable in server-side Next.js API routes), supported only on Chrome Desktop (no Mobile Safari on iOS or Firefox), requires downloading ~1.5–2.4 GB model weights, and adds 500ms–2000ms latency with potential LLM non-determinism.
   - **Alternative:** YouTube video title noise patterns (`(Full Album)`, `[Official Video]`, unmatched `(`, `Remastered`, etc.) are well-defined. A pure TypeScript regex pipeline is sub-millisecond, runs on both server and client, needs 0 setup, and is 100% deterministic.

2. **Cleaning & Repair Pipeline:**
   - HTML entity decoding (`&amp;` → `&`).
   - Bracketed noise tag stripping (`(Full Album)`, `[Official Video]`, `(Official Audio)`, `(Remastered ...)`, etc.).
   - Unmatched/orphaned parenthesis repair (stripping trailing `(` or `[` like in `Physical Graffiti (`).
   - Artist/Title delimiter parsing (`Artist - Title`) and YouTube Topic channel cleaning (`Artist - Topic`).

Please review the plan in [implementation_plan.md](file:///Users/matt/.gemini/antigravity/brain/3a9fb0e7-7ade-4fbb-bda2-5211be5b6e6b/implementation_plan.md). Let me know if you would like me to proceed with implementation!

---

## User

Yeah, but we're talking about using gemini Nano it in the client, because it's a client-side app, and we're talking about only using it if the user happens to have it installed already And then we'll fall back to our patterns which we'll try to do our best

---

## Assistant

That makes complete sense! Using Chrome's `window.ai` (Gemini Nano) as a **client-side progressive enhancement**—only checking if it's already installed and ready on the user's browser, and falling back gracefully to our deterministic regex parser—is a great hybrid approach.

I've updated the implementation plan in [implementation_plan.md](file:///Users/matt/.gemini/antigravity/brain/3a9fb0e7-7ade-4fbb-bda2-5211be5b6e6b/implementation_plan.md) to reflect this hybrid architecture:

1. **Client-side Feature Detection:** Check `('ai' in window)` and `capabilities.available === 'readily'` so it never prompts downloads or blocks execution.
2. **Graceful Fallback:** If `window.ai` is not available, fails, or is on non-Chrome browsers / server side, it instantly uses the robust regex parser.
3. **Deterministic Core:** Regex cleaning handles HTML entity decoding, noise tag stripping `(Full Album)`, `[Official Video]`, and repair of trailing unmatched parens like `Physical Graffiti (`.

Please review [implementation_plan.md](file:///Users/matt/.gemini/antigravity/brain/3a9fb0e7-7ade-4fbb-bda2-5211be5b6e6b/implementation_plan.md) and let me know if you approve proceeding with implementation!

---

## User

As with all plans, I want you to run this by perplexity first. Please resume the original perplexity thread that you used to begin with. Make sure perplexity has all the context of the repo.

---

## Assistant

I ran the plan by Perplexity on our thread, and incorporated its architectural feedback into the plan. Here are the key improvements made:

### Perplexity Architectural Enhancements:
1. **Modern Prompt API Compatibility (`LanguageModel.availability`):**
   - The Prompt API surface was updated in Chrome stable (`LanguageModel.availability()` returning `'available'`). We wrote a feature detector checking the modern global `LanguageModel` first with a fallback to legacy `self.ai.languageModel`, ensuring it never triggers background downloads (`'downloadable'`).
2. **Cancellation & Resource Protection:**
   - Used `AbortSignal` with `AbortController` so timeouts properly abort in-flight AI prompts instead of leaking tasks, and added `session.destroy()` in a `finally` block.
3. **Structured Response Constraint:**
   - Configured `responseConstraint` schema (`{ artist: string, title: string }`) for Prompt API calls so the AI returns clean JSON directly.
4. **Regex Edge Case Refinements:**
   - **Spaced Hyphens:** Splitting on ` - ` (with surrounding spaces) so hyphenated bands like `AC-DC` or `B-52's` are not broken.
   - **CJK Bracket Normalization:** Normalizing full-width Japanese/Korean brackets `（）`, `【】` to ASCII before noise stripping.
   - **Depth-Aware Bracket Repair:** Using bracket depth counting rather than simple string truncation to handle unmatched parens like `Physical Graffiti (`.

The updated plan is saved in [implementation_plan.md](file:///Users/matt/.gemini/antigravity/brain/3a9fb0e7-7ade-4fbb-bda2-5211be5b6e6b/implementation_plan.md). Please let me know if you approve and I can begin implementation!

---

## Assistant

The implementation of the hybrid YouTube video title cleaner and progressive AI parser is complete!

### Summary of Accomplishments

1. **Hybrid Title Parser Module ([`titleParser.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts)):**
   - **Progressive Client AI:** Checks modern Chrome Prompt API (`LanguageModel.availability()`). If Gemini Nano is ready on the user's browser, it parses the title with a 1.5s `AbortController` timeout and structured JSON schema output (`responseConstraint`).
   - **Deterministic Fallback Engine:** Handles HTML entity decoding (`&amp;` → `&`), CJK bracket normalization (`【】` → `[]`), allowlist noise tag stripping (`(Full Album)`, `[Official Video]`, `(Official Audio)`, `(Remastered ...)`), and depth-aware bracket repair to fix dangling parentheses like `Physical Graffiti (`.
   - **Spaced Hyphen & Topic Channel Support:** Parses `Artist - Title` (requiring spaces around hyphens so bands like `AC-DC` aren't split) and strips ` - Topic` suffixes from YouTube channels.

2. **URL Resolver Integration ([`urlResolver.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts)):**
   - Cleaned artist and title metadata are extracted before querying Spotify (`spotapi-service`) and Apple Music (`iTunes API`), preventing search failures on noisy YouTube titles.

3. **Automated Verification ([`titleParser.test.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.test.ts)):**
   - All 9 test cases passed cleanly (`bun test ./app/lib/youtube/titleParser.test.ts`).
   - Specifically verified that `Led Zeppelin - Physical Graffiti (Full Album) [Official Video]` parses to Artist: `Led Zeppelin` and Title: `Physical Graffiti`.

4. **Walkthrough & Log Documentation:**
   - Complete walkthrough available in [walkthrough.md](file:///Users/matt/.gemini/antigravity/brain/3a9fb0e7-7ade-4fbb-bda2-5211be5b6e6b/walkthrough.md).
   - Code changes committed and pushed to git remote.

You can inspect the conversation log anytime in .

---

## User

not fixed still!

---

## User

continue

---

## User

media links work, but the title has an extra `(`

---

## Assistant

### Root Cause Identified & Fixed!

The reason `Physical Graffiti (` was still showing up in the header when pasting a direct YouTube video URL was because:

1. **`app/api/resolve-link/route.ts`** was using a legacy inline string splitter `parseArtistTitleFromVideoTitle` that naively stripped parens from video titles and produced a stale slug stored in `tmp/slugs.json` (`Physical Graffiti (`).
2. **`TrackView.tsx`** was displaying the raw track title from the slug store directly without passing it through `cleanYouTubeTitle`.

### Fixes Applied:

1. **Updated `/api/resolve-link` route ([`route.ts`](file:///Users/matt/projects/music-cross-linker/app/api/resolve-link/route.ts)):**
   - Replaced the legacy string splitter with our new `parseYouTubeTitle` parser so when any YouTube URL is submitted, `title` and `artistName` are sanitized (noise tags stripped and unmatched parens repaired) before generating the canonical URL slug.

2. **Updated `TrackView.tsx` ([`TrackView.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/track-view/TrackView.tsx)):**
   - Wrapped header display titles in `cleanYouTubeTitle` as a safety layer so even cached titles are cleaned before rendering.

3. **Cleared & Healed Stale Cache ([`slugs.json`](file:///Users/matt/projects/music-cross-linker/tmp/slugs.json)):**
   - Corrected the cached record for `led-zeppelin/physical-graffiti` from `"Physical Graffiti ("` to `"Physical Graffiti"`.

All unit tests pass cleanly, and the fix has been committed and pushed to git!

---
