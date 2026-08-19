---
title: "Fixing Search and Track Matching"
date: "2026-08-19"
conversation_id: "97edc11d-6d41-48a5-a1bb-3f82966762e9"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 19, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">when I do a search from the home page, and select a video, I don't get that video, I think I get the very first match instaed.<br>And the slug is just the exact search terms I typed in, hyphenated. It should be a proper slug.<br>Also, when the video title is something like "In my life (Remastered 2009)" we HAVE to pick the 2009 remaster with that same album, we can't be picking stuff from greatest hits, or 2023 mixes, which is what happened for both Spotify AND Apple Music. We should tweak our search algs to prioritize things of the best year, and also parse titles of all kinds of crazy formats.</span>



<span title="Responded at 8:16am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

I have researched the root causes for the video selection mismatch, raw search slug formatting, and the year/remaster mismatch on Spotify and Apple Music, and created a detailed plan in [implementation_plan.md](file:///Users/matt/.gemini/antigravity/brain/97edc11d-6d41-48a5-a1bb-3f82966762e9/implementation_plan.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/97edc11d-6d41-48a5-a1bb-3f82966762e9/implementation_plan.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/97edc11d-6d41-48a5-a1bb-3f82966762e9/implementation_plan.md).

### Summary of Root Causes & Proposed Fixes

1. **Exact Video Selection**:
   - **Root Cause**: When selecting a video from the home page, the app navigated to the YouTube URL, but during slug resolution `/api/resolve-link` matched an existing entity record in `slugStore.ts` that held a previously saved `videoId`. Furthermore, `ResolvingRedirect` dropped the specific video ID during the redirect.
   - **Fix**: Preserve `searchParams.v` during client redirect and in `TrackView`, ensuring the exact video chosen by the user is passed to the player.

2. **Clean Slug Generation**:
   - **Root Cause**: YouTube Topic channel names (`The Beatles - Topic`) were not being stripped during oEmbed resolution, causing slugs to become `the-beatles-topic/in-my-life` or falling back to raw hyphenated search terms.
   - **Fix**: Enhance `parseYouTubeTitle` and `cleanYouTubeTitle` to sanitize channel names, extract proper artist/title pairs, and handle 1-segment hyphenated slugs.

3. **Year & Remaster Prioritization (Spotify & Apple Music)**:
   - **Root Cause**: 
     - In `urlResolver.ts` (Apple Music / iTunes), candidate search only evaluated 5 results and took the first match with normalized title equality—picking the top-ranked recent `2023 Mix` or *Greatest Hits (Red Album)*.
     - In `spotapi-service/main.py` (Spotify), `_normalize` stripped edition suffixes and outtake parentheticals indiscriminately, causing `In My Life (Take 1)` and `2023 Mix` to outrank `In My Life - Remastered 2009`.
   - **Fix**: 
     - Extract rich version metadata (`year`, `isRemaster`, `isMix`, `isLive`, `albumHint`, `isOuttake`).
     - Introduce candidate scoring algorithms in both TypeScript (`urlResolver.ts`) and Python (`spotapi-service/main.py`) that reward year/remaster alignment (+80), penalize conflicting years/mixes (-60), heavily penalize outtakes/demos (`Take 1`, `Demo`, `Acoustic Tribute`), and deprioritize compilations in favor of canonical studio albums (*Rubber Soul*).

Please review the plan in [implementation_plan.md](file:///Users/matt/.gemini/antigravity/brain/97edc11d-6d41-48a5-a1bb-3f82966762e9/implementation_plan.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/97edc11d-6d41-48a5-a1bb-3f82966762e9/implementation_plan.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/97edc11d-6d41-48a5-a1bb-3f82966762e9/implementation_plan.md). Once approved, I will proceed with the implementation and run full automated and manual verifications.

---
*Reference: [thread.md](file:///Users/matt/.gemini/antigravity/brain/97edc11d-6d41-48a5-a1bb-3f82966762e9/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/97edc11d-6d41-48a5-a1bb-3f82966762e9/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/97edc11d-6d41-48a5-a1bb-3f82966762e9/thread.md)*

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | Committed | PPLX Quota | Handoff |
| :--- | :--- | :--- | :--- | :--- |
| ~65k / ~450k 🟢 (optimal) | 3:15am | 🟢 Clean | 89 ❓, 37 📤 | [⚡ -39% context · -25% cost T1](http://127.0.0.1:3031/handoff?session=97edc11d-6d41-48a5-a1bb-3f82966762e9) |

<span style="position: absolute; right: 2rem; bottom: 0.5rem; display: inline-block; font-size: 11px; font-weight: 600; opacity: 0.7; padding: 3px 10px; border: 1px solid rgba(113,100,175,0.4); border-radius: 20px; white-space: nowrap; letter-spacing: 0.3px;"><a href="file:///Users/matt/.gemini/antigravity/brain/97edc11d-6d41-48a5-a1bb-3f82966762e9/kanban.md" style="text-decoration:none;">📋 Kanban</a></span>

</span>

</span>