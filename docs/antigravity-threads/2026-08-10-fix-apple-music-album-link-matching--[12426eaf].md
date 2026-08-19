---
title: "Fix Apple Music album link matching"
date: "2026-08-10"
conversation_id: "12426eafbefc"
source: "antigravity"
---

# Fix Apple Music album link matching

## User

If I type `http://localhost:3011/https://music.apple.com/ca/album/belladonna/1844719636`
then the Apple Music link it gives me is `https://music.apple.com/us/album/desert-rose/1844719636?i=1844719654&uo=4`
I mean, first of all, I pasted an album and it links to a song called desert rose ON that album. we want to link to the album.
second, it's a US link when I pasted a Canadian link.
Third, I PASTED the fucking link so why wouldn't it use MY link for Apple Music?! (that should be the case for all platforms; if I paste a YouTube link, just embed that video... don't show Youtube search results either; if I paste Spotify link, use that for Spotify).

---

## Assistant

I am going to inspect the codebase structure in `/Users/matt/projects/music-cross-linker` to see how incoming URLs are parsed, processed, and matched across platforms.

I will now test the Odesli API response and inspect the rest of the helper modules (`apple-music.ts`, `spotify.ts`, `youtube.ts`) to see how entity metadata and URLs are currently resolved.

[Proxy Error]: LiteLLM returned 500: {"error":{"message":"litellm.InternalServerError: Vertex_ai_betaException InternalServerError - b'{\\n  \"error\": {\\n    \"code\": 500,\\n    \"message\": \"Internal error encountered.\",\\n    \"status\": \"INTERNAL\"\\n  }\\n}\\n'","type":null,"param":null,"code":"500"}}

---

## User

continue

---

## Assistant

`⚙️ running run_command`
`✅ run_command done`
`⚙️ running define_subagent`
`✅ define_subagent done`I have spawned the file editor subagent to apply the updates to `app/lib/odesli.ts`, `app/lib/urlResolver.ts`, `app/[...url]/page.tsx`, and `app/[artist]/[track]/page.tsx`. I will wait for it to complete.

`⚙️ running manage_subagents`
`✅ manage_subagents done`
`⚙️ running run_command`
`✅ run_command done`
`⚙️ running run_command`
`✅ run_command done`
`⚙️ running run_command`
`✅ run_command done`
`⚙️ running run_command`
`✅ run_command done`
`⚙️ running run_command`
`✅ run_command done`
`⚙️ running run_command`
`✅ run_command done`
`⚙️ running manage_task`
`✅ manage_task done`
`⚙️ running run_command`
`✅ run_command done`
`⚙️ running manage_task`
`✅ manage_task done`
`⚙️ running schedule`
`✅ schedule done`I am waiting for `pnpm run build` to finish compiling to verify that all TypeScript types and Next.js routes validate cleanly.

`⚙️ running manage_task`
`✅ manage_task done`I will wait for the build process notification to arrive once Next.js completes compiling.

`⚙️ running run_command`
`✅ run_command done`The changes are in place and verified with a clean `pnpm run build` compilation:

1. **Preserving User-Pasted Source URLs (`src` propagation)**:
   - When you open `/http://localhost:3011/https://music.apple.com/ca/album/belladonna/1844719636`, `[...url]` extracts the input URL and appends it as `?src=${encodeURIComponent(url)}` onto the track page redirect.
   - `TrackPage` reads the `src` search param and passes it directly to `getPlatformLinks`.

2. **Apple Music Album & Region Handling**:
   - If the user pastes an Apple Music link (`music.apple.com/ca/album/...`), that link is set as `appleUrl` for Apple Music rather than running a fallback iTunes US API lookup that transforms it to a US song link.
   - Cleaned up Odesli's `geo.music.apple.com` links into standard `music.apple.com` links.

3. **Universal Platform Matching**:
   - If you paste a Spotify link, it is preserved for Spotify.
   - If you paste a YouTube link, `youtubeUrl` is set to that exact link and embedded directly into the player iframe without falling back to YouTube search.

---

## User

for some reason, there's TWO YouTube embeds.
Also, we used to have an actual MATCH on Spotify; but now, the exact same album and same link results in just a Spotify search...  what happened there?

---

## Assistant

I am going to check `app/[artist]/[track]/page.tsx` to fix the duplicate YouTube embed render and inspect `app/lib/urlResolver.ts` and `app/lib/odesli.ts` to see why Spotify matching stopped returning direct links.
I've launched the subagent to remove the duplicate YouTube embed block from `TrackPage` and fix the `type` / Odesli cross-platform resolution logic so Spotify album links match directly.

---
