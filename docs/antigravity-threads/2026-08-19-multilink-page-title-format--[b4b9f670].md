---
title: "Multilink Page Title Format"
date: "2026-08-19"
conversation_id: "b4b9f670-60ad-4b1c-81c9-4315e2637e96"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">>Zero-maintenance iframe embed (youtube-nocookie.com): Lightweight, uses zero VPS resources, suppresses behavioral tracking ads, but may occasionally play a standard channel ad.<br><br>standard channel ad?</span>



<span title="Responded at 7:59am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

When a video or song on YouTube is monetized, there are two types of ads YouTube can serve:

---

### 1. Personalized / Behavioral Ads (What `youtube-nocookie.com` stops)
- **How they work**: Google tracks your browsing history across the web using cookies (e.g., you searched for shoes yesterday, so a shoe commercial plays before your song).
- **With `youtube-nocookie.com`**: Google is blocked from reading or setting tracking cookies. It **cannot serve personalized behavioral ads**.

---

### 2. Contextual / Channel Monetization Ads (Why you heard an ad)
- **How they work**: Major record labels (Universal Music, Sony, Warner) and creators enable monetization on their channels via YouTube’s Content ID.
- **Why they play**: Even without cookies, YouTube’s ad server can still serve a **generic, non-personalized commercial** (e.g., a standard car or insurance ad) simply because the record label enabled ads on that specific song.

---

### In Practice
- **On desktop with an ad blocker** (uBlock Origin / Brave): The ad blocker catches the script and it plays instantly without ads.
- **On mobile without an ad blocker** (e.g., clicking a link in iMessage/SMS on an iPhone): YouTube's player will occasionally run the record label's non-personalized pre-roll ad before the music starts.

</span>



</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">is it possible for us to detect when an ad comes and fall back to our streaming backend?</span>



<span title="Responded at 7:58am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The short answer is **no**, due to browser security boundaries and Google’s API design:

---

### 1. The Cross-Origin Security Wall (Same-Origin Policy)
The YouTube player runs inside an `<iframe>` hosted on `youtube-nocookie.com`. 

Because your website (`music.mattmurphy.ca`) and YouTube are on different domains, the browser’s **Same-Origin Policy** strictly blocks your JavaScript from:
- Reading the HTML/DOM inside the iframe (e.g. searching for ad elements like `.ytp-ad-module` or ad skip buttons).
- Inspecting network requests or video stream URLs inside the player.

---

### 2. YouTube’s IFrame API Intentionally Hides Ads
YouTube provides an official JavaScript postMessage bridge ([YouTube IFrame Player API](https://developers.google.com/youtube/iframe_api_reference)), but Google specifically engineered it to prevent ad detection:
- When an ad plays, the API reports `state: 1 (PLAYING)` — identical to normal music playback.
- Ad metadata, ad timers, and ad triggers are completely hidden from the parent page so third-party sites cannot build automated ad-skippers.

---

### 3. The Irony of the Fallback
If you built a VPS streaming backend to serve as a fallback, you wouldn't need the YouTube iframe or ad detection in the first place:
- **Raw audio streams have zero ads from second zero** because you never download or execute YouTube's ad-serving player script.
- If you have the backend, it makes sense to use the custom `<audio>` player directly rather than playing an iframe and attempting to detect ads.

---

### Summary
Trying to sniff ads inside a Google iframe is blocked by browser security and API design. The choice is binary:
1. **Zero-maintenance iframe embed (`youtube-nocookie.com`)**: Lightweight, uses zero VPS resources, suppresses behavioral tracking ads, but may occasionally play a standard channel ad.
2. **Direct audio player via VPS**: 100% ad-free audio, but requires maintaining stream extraction against YouTube's anti-bot updates.

</span>



</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">With option A, are you telling me that for anybody that clicks play on one of our links in messages, we need to have our VPS open up that YouTube link and then stream the audio over? First of all, isn't that difficult to do? And second of all, that can't scale well, can it? I mean I can't imagine You can have more than a few videos Playing and streaming At once</span>



<span title="Responded at 7:54am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

You've hit on two crucial engineering realities: **bandwidth scaling** and **maintenance fragility**.

---

### 1. How Audio Extraction Actually Scales (The Bandwidth Reality)

When web apps extract YouTube streams, they generally don't download, transcode, and re-stream the audio bytes through the VPS.

1. **Direct CDN Streaming (0 VPS Bandwidth)**:
   - The VPS only performs a fast (~50ms) metadata handshake to grab Google's direct raw audio stream URL (`https://*.googlevideo.com/videoplayback?...`).
   - The VPS hands that URL to the visitor's browser `<audio src="...">`.
   - The visitor's phone streams the audio **directly from Google's servers**, not from your VPS. The VPS only serves a few kilobytes of JSON.

2. **If Proxying the Bytes**:
   - Standard music audio (Opus / AAC at 128–160 kbps) is only **~1.2 MB per minute** (~3.5 MB for an entire song).
   - Even on a basic 1 Gbps connection, serving 160 kbps audio can handle hundreds of concurrent listeners using only a fraction of network capacity.

---

### 2. The Real Catch: Maintenance & YouTube's "Cat-and-Mouse" Game

While bandwidth isn't the bottleneck, **fragility is**:

- **Google's Anti-Bot Measures**: YouTube frequently updates its player algorithms, PoTokens (Proof of Origin tokens), and IP rate-limits on datacenter/VPS IPs.
- **Maintenance Burden**: Running a custom audio extraction backend requires constantly updating extraction libraries (`yt-dlp`, Piped API, etc.) whenever YouTube rotates their cipher signatures.

---

### 3. What Makes Sense for Multilink

**Multilink’s core value is being the universal music bridge**:
- When someone opens your link in Messages, the goal is to give them **instant 1-tap access to open the track in their native platform** (Apple Music, Spotify, or YouTube).
- The player on the page is a convenient preview.

### Recommendation
**Stick with the `youtube-nocookie.com` embed we just deployed.**
- **Zero VPS load & Zero bandwidth costs** (Google serves everything).
- **Zero maintenance fragility** (won't break when YouTube changes their player backend).
- **Drastically reduced ads & tracking** compared to standard YouTube embeds.
- Directs users naturally to their primary music app (Spotify / Apple Music) where they get their ad-free, lossless music experience.

</span>



</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">ok, wow, I'm impressed that we're able to actually PLAY audio, that's sick.<br>But we have a REAL problem: when I clicked play, I heard an ad play. We GOTTA stop that!<br>I mean, fuck do we have to like integrate ublock origin or something? what a bummer</span>



<span title="Responded at 7:52am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

### Why YouTube Embeds Show Ads

Standard YouTube `<iframe>` embeds (`youtube.com/embed/...`) run YouTube's proprietary player scripts, which dynamically inject pre-roll and mid-roll video ads on monetized videos unless the client running the browser has an ad blocker extension installed.

---

### What Was Done Immediately

1. **Migrated to `youtube-nocookie.com`**:
   All iframe players ([`YouTubeSection.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/track-view/YouTubeSection.tsx#L24) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/components/track-view/YouTubeSection.tsx%3A24) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/components/track-view/YouTubeSection.tsx), [`YouTubePlayer.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/track-view/YouTubePlayer.tsx#L41) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/components/track-view/YouTubePlayer.tsx%3A41) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/components/track-view/YouTubePlayer.tsx), [`ResolvingRedirect.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/ResolvingRedirect.tsx#L65) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/components/ResolvingRedirect.tsx%3A65) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/components/ResolvingRedirect.tsx)) have been switched to Google's Privacy-Enhanced domain with clean flags:
   ```html
   https://www.youtube-nocookie.com/embed/${videoId}?autoplay=0&rel=0&modestbranding=1&iv_load_policy=3
   ```
   This disables tracking cookies and strips personalized behavioral ad targeting.

---

### How To Achieve 100% Guaranteed Ad-Free Playback

If you want **zero ads ever** on any device (including mobile Safari/Chrome without uBlock Origin), there are two distinct architectural approaches:

#### Option A: Custom HTML5 Audio Player via Self-Hosted VPS Stream *(Recommended)*
- **How it works**: Since we already run the Oracle VPS (`vps.mattmurphy.ca`) for `spotapi-service`, we can add a lightweight audio extraction endpoint (via `yt-dlp` or Piped stream API).
- **The Experience**: Instead of embedding a YouTube iframe, the page renders a custom, sleek glassmorphic audio player (`<audio>` with custom waveform/scrubber, play/pause, and time controls).
- **Result**:
  - **100% Ad-Free**: YouTube ad scripts are never downloaded or executed.
  - **Faster Load Times**: No heavy YouTube iframe or bloated Google tracking bundles.
  - **Background Audio**: Allows background audio playback on mobile browsers without YouTube pausing when the screen locks.

#### Option B: Piped / Invidious Privacy Frontend Embed
- **How it works**: Embed a self-hosted or public Piped / Invidious player iframe (e.g. `piped.video/embed/${videoId}`).
- **The Experience**: Keeps the full video player UI, but proxies the video stream through an ad-stripped open-source frontend.

---
- **Thread Context**: [thread.md](file:///Users/matt/.gemini/antigravity/brain/b4b9f670-60ad-4b1c-81c9-4315e2637e96/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/b4b9f670-60ad-4b1c-81c9-4315e2637e96/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/b4b9f670-60ad-4b1c-81c9-4315e2637e96/thread.md)
- **Project Board**: [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)
- **Agent Log**: [`agent-logs/2026-08-19_01-53_youtube-nocookie-privacy-embeds.md`](file:///Users/matt/projects/music-cross-linker/agent-logs/2026-08-19_01-53_youtube-nocookie-privacy-embeds.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/agent-logs/2026-08-19_01-53_youtube-nocookie-privacy-embeds.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/agent-logs/2026-08-19_01-53_youtube-nocookie-privacy-embeds.md)

</span>



</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">ooh, when you share a youtube link Apple Messages, it gives a little preview image, you know? Can we make that the thumbnail of the highest resolution image we have of the most certain match?<br>And if you give a YouTube link in Apple Messages, you can play it directly in chat. I don't suppose that's the on the table?</span>



<span title="Responded at 7:50am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

### 1. High-Resolution Preview Artwork (`og:image`)

Implemented in [`app/lib/urlResolver.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts#L756) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts%3A756) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/urlResolver.ts) and [`app/[...url]/page.tsx`](file:///Users/matt/projects/music-cross-linker/app/[...url]/page.tsx#L55):

- **Apple Music**: Scaled from the 100px thumbnail up to **`1200x1200bb`** (lossless high-res square album art from Apple's CDN).
- **Spotify**: Uses the **640x640** square album art from Spotify's CDN.
- **YouTube**: Extracted as **`maxresdefault.jpg`** (1280×720 high-res preview thumbnail).
- The matcher prioritizes authoritative / high-confidence platform matches first, providing a crisp, full-bleed rich card when sharing links via Apple Messages, Slack, Discord, Twitter/X, and WhatsApp.

---

### 2. Can you play YouTube inline directly inside Apple Messages chat?

**The short answer:** Unfortunately not for custom 3rd-party domain links in Apple Messages.

**Why:**
- Apple Messages renders rich links using WebKit's private **`LinkPresentation.framework`** (`LPLinkMetadata`).
- iOS/macOS strictly limits interactive in-chat inline video and audio playback to:
  1. Whitelisted first-party domains (e.g. raw `youtube.com`, `music.apple.com`, `spotify.com` audio clips).
  2. Direct video/audio file streams (e.g. `.mp4`, `.mov`, `.m4a` files).
- For all 3rd-party web pages, Apple Messages will not execute external `<iframe>` embeds inside the chat thread for sandboxing and security reasons.

**What we did provide:**
- Added standard OpenGraph video tags (`og:video`, `og:video:secure_url`, `og:video:type="text/html"`, `og:video:width="1280"`, `og:video:height="720"`) and Twitter Large Card metadata.
- In Apple Messages, this produces a prominent rich preview card with the high-resolution artwork and title that opens directly to the auto-playing YouTube embed and cross-platform links on tap.
- In apps that *do* support OpenGraph video embedding (Discord, Telegram, etc.), the video can be played inline right from chat.

---
- **Thread Context**: [thread.md](file:///Users/matt/.gemini/antigravity/brain/b4b9f670-60ad-4b1c-81c9-4315e2637e96/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/b4b9f670-60ad-4b1c-81c9-4315e2637e96/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/b4b9f670-60ad-4b1c-81c9-4315e2637e96/thread.md)
- **Project Board**: [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)
- **Agent Log**: [`agent-logs/2026-08-19_01-51_high-res-thumbnail-and-og-video.md`](file:///Users/matt/projects/music-cross-linker/agent-logs/2026-08-19_01-51_high-res-thumbnail-and-og-video.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/agent-logs/2026-08-19_01-51_high-res-thumbnail-and-og-video.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/agent-logs/2026-08-19_01-51_high-res-thumbnail-and-og-video.md)

</span>



</span>

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 19, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">When I share a page, I need the title of the page to be "Artist - Album/Track | Multilink" or something. idk about multilink but it's the best I can come up with right now. It quickly conveys that it's a page with multiple links, and one would assume media links. idk it's not so heavy</span>



<span title="Responded at 7:32am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The page title and sharing metadata have been updated across the application.

### Summary of Changes

1. **Title & Share Metadata Formatting ([`app/lib/youtube/titleParser.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts))**:
   - Added [`buildPageTitle(artist, track)`](file:///Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts#L225) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts%3A225) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts) and [`buildPageDescription(artist, track)`](file:///Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts#L241) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts%3A241) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts):
     - With artist & track/album: `"Artist - Album/Track | Multilink"` (e.g. `Daniel Lanois - Belladonna | Multilink`, `Daft Punk - Alive 2007 | Multilink`).
     - With track/album only: `"Album/Track | Multilink"` (e.g. `Belladonna | Multilink`).
     - Fallback / Root: `"Multilink - Universal Music Links"`.
   - Strips noise tags (e.g. `[Official Video]`, `(Full Album)`) before constructing the title for clean presentation on shared link previews.

2. **Dynamic Metadata Resolution ([`app/[...url]/page.tsx`](file:///Users/matt/projects/music-cross-linker/app/[...url]/page.tsx))**:
   - Added [`generateMetadata`](file:///Users/matt/projects/music-cross-linker/app/[...url]/page.tsx#L12) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/%5B...url%5D/page.tsx%3A12) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/%5B...url%5D/page.tsx) to dynamically extract and format metadata for shared routes:
     - Stored slug records (via [`getRecordBySlug`](file:///Users/matt/projects/music-cross-linker/app/lib/slugStore.ts#L110) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/slugStore.ts%3A110) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/slugStore.ts)).
     - Route parameters (`/album/artist/track`, `/track/artist/track`, `/artist/track`, `/track`).
     - External URL lookups (via [`findRecordByTargetUrlOrVideo`](file:///Users/matt/projects/music-cross-linker/app/lib/slugStore.ts#L115) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/slugStore.ts%3A115) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/slugStore.ts)).
   - Sets absolute `<title>`, `description`, OpenGraph (`og:title`, `og:description`, `og:site_name: "Multilink"`), and Twitter card metadata.

3. **Layout Default Metadata ([`app/layout.tsx`](file:///Users/matt/projects/music-cross-linker/app/layout.tsx) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/layout.tsx) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/layout.tsx))**:
   - Configured default title and title template (`%s | Multilink`).

4. **Testing & Verification**:
   - Added test coverage in [`app/lib/youtube/titleParser.test.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.test.ts) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.test.ts) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.test.ts). All 18 unit tests passing.
   - Verified clean production build with Turbopack and TypeScript.
   - Changes committed and pushed to remote.

---
- **Thread Context**: [thread.md](file:///Users/matt/.gemini/antigravity/brain/b4b9f670-60ad-4b1c-81c9-4315e2637e96/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/b4b9f670-60ad-4b1c-81c9-4315e2637e96/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/b4b9f670-60ad-4b1c-81c9-4315e2637e96/thread.md)
- **Project Board**: [PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/PROJECT_BOARD.md)
- **Agent Log**: [`agent-logs/2026-08-19_01-33_page-title-and-share-metadata.md`](file:///Users/matt/projects/music-cross-linker/agent-logs/2026-08-19_01-33_page-title-and-share-metadata.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/agent-logs/2026-08-19_01-33_page-title-and-share-metadata.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/agent-logs/2026-08-19_01-33_page-title-and-share-metadata.md)

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | Committed | PPLX Quota | Handoff |
| :--- | :--- | :--- | :--- | :--- |
| ~120k / ~450k 🟡 (fatigue) | 3:00am | 🟢 Clean | 89 ❓, 37 📤 | [⚡ -59% context · -10% cost T1](http://127.0.0.1:3031/handoff?session=b4b9f670-60ad-4b1c-81c9-4315e2637e96) |

<span style="position: absolute; right: 2rem; bottom: 0.5rem; display: inline-block; font-size: 11px; font-weight: 600; opacity: 0.7; padding: 3px 10px; border: 1px solid rgba(113,100,175,0.4); border-radius: 20px; white-space: nowrap; letter-spacing: 0.3px;"><a href="file:///Users/matt/.gemini/antigravity/brain/b4b9f670-60ad-4b1c-81c9-4315e2637e96/kanban.md" style="text-decoration:none;">📋 Kanban</a></span>

</span>

</span>