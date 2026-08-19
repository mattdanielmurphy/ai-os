---
title: "User Request: We want to extract high-resolution album cover artwork reliably..."
date: "2026-08-14"
conversation_id: "b993d675-93f9-4f84-b656-95095a8005c7"
source: "antigravity"
---

# User Request: We want to extract high-resolution album cover artwork reliably...

## User

User Request: We want to extract high-resolution album cover artwork reliably and derive a vibrant full-page gradient background from its dominant non-black/non-gray colors. Currently: 1. getBestAlbumArt in TrackView.tsx runs synchronously on initial render using only ctx.cached, which is empty before AppleSection or SpotifySection resolve via Suspense. Therefore albumArt is missing or falls back to YouTube thumbnail URLs or nothing on initial load. 2. ctx.cached.apple_music.url is an Apple Music webpage link, NOT an image URL. 3. YouTube video URLs are letterboxed video stills or video frames (e.g. Prince live video), not true album covers, yielding black/dark backgrounds. We need an architectural architecture plan for: (a) Fetching real artwork image URLs from iTunes Search / Apple Music Lookup API or Spotify oEmbed / API endpoints (or storing artwork_url directly in match_candidates / entity_matches). (b) Streaming or client-side/server-side palette extraction so that as soon as Apple Music or Spotify matches resolve, the page updates its background gradient with vibrant album artwork colors. (c) Fallback artwork image fetching by running a server-side iTunes artwork lookup on ctx.searchTerm if no cached artwork image URL is present yet.

Target GitHub Repository: mattdanielmurphy/music-cross-linker
Please query the GitHub connector for repository source code and documentation for repo 'mattdanielmurphy/music-cross-linker' if needed.

Please act as a senior planner. Analyze the request and output a detailed architectural implementation plan for the orchestrator.

---

## Assistant

## Perplexity — 06:36 PM

Architecture Plan: Real Artwork Resolution + Streaming Vibrant Gradients

The core problem is a **timing and data-shape mismatch**: `getBestAlbumArt` runs before Suspense boundaries resolve, and even when they do resolve, the cached values (`apple_music.url`) are webpage links, not images, forcing a fallback to YouTube video stills that are frequently black/letterboxed. Fixing this requires changes at three layers — data model, server-side fetch/caching, and client streaming — plus a dedicated color-extraction pipeline. Below is the full plan.

1. Data Model Changes

Add a dedicated image field to the matching tables so artwork URLs are persisted independently of the platform "canonical link," and add a palette cache so extraction never has to be redone.

Table	New column	Purpose
`match_candidates`	`artwork_url text`	High-res image URL captured at match time (iTunes `artworkUrl100`-derived or Spotify `images[0].url`)
`match_candidates`	`artwork_source text`	`'itunes' \| 'spotify_oembed' \| 'spotify_api' \| 'youtube_fallback'` — lets the client rank trust
`entity_matches`	`artwork_url text`, `artwork_palette jsonb`	Resolved artwork for the canonical entity + cached extracted colors `{ vibrant, muted, dominant[] }`
`entity_matches`	`artwork_fetched_at timestamptz`	TTL for re-validating stale/expired mzstatic/scdn URLs

Migration goes in `migrations/` (repo already uses a SQL migration folder against what is almost certainly the Supabase Postgres instance). Backfill existing rows lazily — don't block deploy on a full backfill job; populate on next read via the fallback lookup described in §3.

2. Server-Side Artwork Resolution Layer

Create a single server module, e.g. `app/lib/artwork.ts`, with three resolver functions, each normalized to return `{ url, width, height, source }` or `null`. This is the single source of truth every caller (Apple resolver, Spotify resolver, fallback API route) uses.

**iTunes Lookup/Search resolver** — call `https://itunes.apple.com/lookup?id={appleId}&entity=song` (or `/search` if only a search term is available). The response's `artworkUrl100` field must be upsized by string substitution — replace `100x100bb` with a larger token like `1200x1200bb`, since Apple serves any resolution from the same CDN path. Do not use `apple_music.url` (the webpage link) as an image source at all — it should be removed from any artwork-selection logic in `getBestAlbumArt`.
developer.apple
+1

**Spotify resolver** — prefer the standard Web API `album.images[]` array (returns multiple sizes, largest first, typically 640×640) when you already have a Spotify track/album ID and an access token. If no token/ID is available yet (e.g., only a Spotify URL was cached), fall back to the public oEmbed endpoint `https://open.spotify.com/oembed?url={spotifyUrl}`, which needs no auth and returns `thumbnail_url` directly.
developer.spotify
+1

**Apple Music Catalog artwork template resolver** (if using the authenticated Apple Music API rather than the free iTunes Search API) — note the `artwork.url` field is a *template* containing literal `{w}x{h}` placeholders that must be substituted before use, e.g. `artwork.url.replace('{w}x{h}', '1200x1200')`.
audd

All three resolvers should write their result back into `match_candidates.artwork_url` / `entity_matches.artwork_url` immediately (fire-and-forget upsert), so the next request for the same track is a cache hit and skips the network call entirely.

3. Fallback Route for Missing Artwork

Add `app/api/artwork/fallback/route.ts` (server-side, Node runtime) that:

Accepts `searchTerm` (the same term `ctx.searchTerm` uses for platform matching) and optional `entityId`.

Runs `https://itunes.apple.com/search?term={searchTerm}&entity=album&limit=1`, upsizes `artworkUrl100`, and returns the URL.

Persists the result to `entity_matches.artwork_url` keyed by `entityId` if provided, so the lookup happens at most once per entity.

Rate-limits/debounces per IP or per-track to avoid hammering the iTunes API when many unmatched tracks hit the page simultaneously (simple in-memory or Redis token bucket is enough; iTunes has an undocumented ~20 req/min soft cap per IP).

This route is the safety net: it fires whenever the client determines that neither Apple nor Spotify has produced an `artwork_url` after a short grace period (see §4), independent of whether those platform matches ever resolve.

4. Client Streaming Architecture

Replace the synchronous, cache-only `getBestAlbumArt` call with a **reactive artwork resolution pipeline** that updates as each Suspense boundary settles, rather than computing once on initial render.

**Introduce an `AlbumArtProvider` context** (client component) wrapping `TrackView`, holding:


```
ts
type ArtworkState = {
  url: string | null
  source: 'cache' | 'apple' | 'spotify' | 'fallback' | 'youtube' | null
  status: 'idle' | 'loading' | 'resolved' | 'exhausted'
}
```


**Resolution priority order** (re-evaluated every time a child resolves):

Priority	Source	Condition
1	`ctx.cached.entity_matches.artwork_url`	Already persisted from a prior resolution — instant, no flash
2	Apple Music resolver result	`AppleSection` Suspense boundary resolves and returns a real image URL
3	Spotify resolver result	`SpotifySection` Suspense boundary resolves and returns a real image URL
4	Server fallback route (§3)	Triggered client-side after ~800ms if priorities 1–3 haven't produced a URL
5	YouTube thumbnail	Only as an absolute last resort, and only after checking it isn't a letterboxed still (see filter below)

**Wiring mechanism:** each of `AppleSection` and `SpotifySection`, instead of only rendering platform links, should call a `reportArtwork(url, source)` callback (passed down or dispatched via the context) as a side effect once their own data resolves inside the Suspense boundary. Because React Suspense streams independently, `AppleSection` may resolve well before `SpotifySection` or vice versa — the context should accept whichever arrives first and only overwrite if a *higher-priority* source arrives later (Apple/Spotify real image beats a stale YouTube-derived guess).

Trigger the §3 fallback with a `useEffect` timer inside `AlbumArtProvider`: if `status === 'loading'` after the grace window, call `/api/artwork/fallback?searchTerm=...` and update state on response. This guarantees the page never stays on a black/YouTube background for more than ~1 second even if both platform matches are slow or fail.

5. Palette Extraction Pipeline

Extraction should happen **server-side once, cached forever**, not recomputed client-side on every page view — this keeps the gradient update fast and avoids CORS/canvas-tainting issues with cross-origin mzstatic/scdn images.

**Where:** a server function (can live in the same `app/lib/artwork.ts` or a sibling `app/lib/palette.ts`), invoked immediately after any resolver in §2 writes a new `artwork_url`. Use `node-vibrant` (or `colorthief`+`sharp` if you want fewer deps) to extract a swatch palette from the image buffer.

**Filtering black/gray for vibrancy:** after extraction, discard swatches where:

Saturation < ~0.15 (grays), or

Lightness < ~0.12 or > ~0.92 (near-black/near-white)

Rank remaining swatches by `population × saturation` and keep the top 2–3 for the gradient stops. Store the filtered result in `entity_matches.artwork_palette` as `{ vibrant: "#rrggbb", secondary: "#rrggbb", muted: "#rrggbb" }` so subsequent page loads skip extraction entirely.

**Streaming to the client:** once `AlbumArtProvider`'s state moves to `resolved` with a URL that also has a cached `artwork_palette`, apply the gradient immediately (no extraction needed). If the palette isn't cached yet (first-ever resolution for that entity), do a **lightweight client-side extraction** using a hidden `<canvas>` and `ColorThief` on the just-resolved image as an interim gradient while the server-side extraction (triggered async on that image) backfills the cache for next time. This gives an instant vibrant background on the very first visit without waiting on a round trip, while still converging to the canonical cached palette for all future visits.

6. Rollout Sequencing

Ship the DB migration (additive columns, non-breaking).

Ship the resolver module + fallback route behind a feature flag; log resolution source/latency to catch cases where iTunes/Spotify calls are slow or rate-limited.

Swap `getBestAlbumArt` for the `AlbumArtProvider`-driven state; keep the old function as a synchronous "instant paint" fallback only for `ctx.cached` hits so there's no regression in perceived speed for already-cached tracks.

Add the black/gray filter and gradient CSS (`background: linear-gradient(...)` driven by the palette state) last, once artwork resolution itself is verified reliable — this isolates whether any remaining "dark background" complaints are an artwork problem or a color-extraction problem.

This gives you: correct high-res images from the actual artwork APIs instead of webpage links or video stills, progressive gradient updates as each platform section streams in via Suspense, and a guaranteed fallback path keyed on `ctx.searchTerm` so no track ever gets stuck without artwork.
developer.apple
+2

---
