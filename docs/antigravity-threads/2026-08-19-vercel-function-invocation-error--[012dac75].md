---
title: "Vercel Function Invocation Error"
date: "2026-08-19"
conversation_id: "012dac75-79ac-491c-8814-5d10a299691c"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw - 2px); bottom: 0; padding: 2.5rem calc(2rem) 2.5rem calc(2rem + 2 * 2px); scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 19, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; margin-bottom: 48px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 10px 14px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.45; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">I've got a problem with the vercel deployment:<br># GET /the-bombay-royale/henna-henna<br><br>Status: 500 (FUNCTION_INVOCATION_FAILED)<br><br>## Request<br><br>Started: Aug 19 02:44:45.74 GMT-6<br><br>Request ID: 9jnfk-1787129085744-387bc7ac9624<br><br>Path: /the-bombay-royale/henna-henna<br><br>Host: music.mattmurphy.ca<br><br>User Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36<br><br>Search Params<br><br>- nxtPurl=the-bombay-royale/henna-henna<br><br>Error Code: FUNCTION_INVOCATION_FAILED<br><br>Received in Portland, USA (pdx1)<br><br>### Firewall<br><br>Allowed<br><br>Routed to Washington, D.C., USA (iad1)<br><br>### Function Invocation<br><br>Route: /[...url]<br><br>Error Page: /500<br><br>Execution Duration: 11ms<br><br>### External APIs<br><br>Loading...<br><br>Awaiting data<br><br>### Fluid<br><br>244 MB<br><br>Response finished in 218ms<br><br>## Deployment Information<br>Deployment ID: dpl_8tp6o9msnwV9vtDj9bTQkwHveRN7<br>Environment: production<br>Branch: main</span>



<span title="Responded at 8:47am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

### Root Cause

Inspecting the Vercel serverless function logs for deployment `dpl_8tp6o9msnwV9vtDj9bTQkwHveRN7` revealed the exact failure:

```
Error: Failed to load external module sharp: Error: Could not load the "sharp" module using the linux-x64 runtime 
ERR_DLOPEN_FAILED: libvips-cpp.so.8.18.3: cannot open shared object file: No such file or directory
```

Because `sharp` is a native C++ module requiring platform-specific shared libraries (`libvips-cpp`), top-level `import sharp from 'sharp'` in [`app/lib/palette.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/palette.ts) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/palette.ts) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/palette.ts) caused Vercel's Linux x64 serverless runtime to crash during module initialization (`FUNCTION_INVOCATION_FAILED` in 11ms) before any page route handler could execute.

---

### Changes Made

1. **Replaced Native `sharp` with Zero-Native Pure JS Decoders**:
   - Swapped `sharp` for pure JavaScript decoders [`jpeg-js`](https://github.com/eugeneware/jpeg-js) and [`pngjs`](https://github.com/lukeapage/pngjs) in [`app/lib/palette.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/palette.ts) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/palette.ts) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/palette.ts).
   - Implemented [`decodeImageToRgba()`](file:///Users/matt/projects/music-cross-linker/app/lib/palette.ts#L390) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/palette.ts%3A390) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/palette.ts) with magic-byte format sniffing (JPEG `FF D8`, PNG `89 50 4E 47`) and fallback decoding.
   - Added lightweight in-memory grid step-sampling [`sampleImageBufferToGrid()`](file:///Users/matt/projects/music-cross-linker/app/lib/palette.ts#L434) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/palette.ts%3A434) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/palette.ts) to downsample artwork directly to an 80×80 raw pixel buffer with 0 native C++ dependencies.

2. **Configuration & Dependencies**:
   - Added `jpeg-js`, `pngjs`, and `@types/pngjs` to [`package.json`](file:///Users/matt/projects/music-cross-linker/package.json) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/package.json) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/package.json).
   - Removed `sharp` from dependencies and ignore scripts.
   - Configured `serverExternalPackages: ["postgres"]` in [`next.config.ts`](file:///Users/matt/projects/music-cross-linker/next.config.ts) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/next.config.ts) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/next.config.ts).

3. **Validation & Deployment**:
   - Ran `bun test`: all 32 unit tests pass in [`app/lib/palette.test.ts`](file:///Users/matt/projects/music-cross-linker/app/lib/palette.test.ts) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/music-cross-linker/app/lib/palette.test.ts) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/music-cross-linker/app/lib/palette.test.ts).
   - Ran `bun run build`: Next.js Turbopack production build succeeded cleanly.
   - Staged, committed, and pushed changes to remote via [`auto_commit.py`](file:///Users/matt/projects/ai-os/scripts/auto_commit.py) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/scripts/auto_commit.py) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/scripts/auto_commit.py) (commit `175800a`), triggering a fresh Vercel deployment.

---

Conversation transcript: [thread.md](file:///Users/matt/.gemini/antigravity/brain/012dac75-79ac-491c-8814-5d10a299691c/thread.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/.gemini/antigravity/brain/012dac75-79ac-491c-8814-5d10a299691c/thread.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/.gemini/antigravity/brain/012dac75-79ac-491c-8814-5d10a299691c/thread.md)

</span>



</span>

<span style="position: absolute; left: 0; right: 0; bottom: 0; width: 100cqw; padding: 0 2rem;">

| Tokens | Expiry | Committed | PPLX Quota | Handoff |
| :--- | :--- | :--- | :--- | :--- |
| ~70k / ~450k 🟢 (optimal) | 3:45am | 🟢 Clean | 90 ❓, 37 📤 | [⚡ -43% context · -22% cost T1](http://127.0.0.1:3031/handoff?session=012dac75-79ac-491c-8814-5d10a299691c) |

<span style="position: absolute; right: 2rem; bottom: 0.5rem; display: inline-block; font-size: 11px; font-weight: 600; opacity: 0.7; padding: 3px 10px; border: 1px solid rgba(113,100,175,0.4); border-radius: 20px; white-space: nowrap; letter-spacing: 0.3px;"><a href="file:///Users/matt/.gemini/antigravity/brain/012dac75-79ac-491c-8814-5d10a299691c/kanban.md" style="text-decoration:none;">📋 Kanban</a></span>

</span>

</span>