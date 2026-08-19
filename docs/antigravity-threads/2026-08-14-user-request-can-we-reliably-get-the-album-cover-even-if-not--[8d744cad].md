---
title: "User Request: Can we reliably get the album cover? Even if not, we should pick..."
date: "2026-08-14"
conversation_id: "8d744cad-4176-4389-ac14-55b7e24fcfbf"
source: "antigravity"
---

# User Request: Can we reliably get the album cover? Even if not, we should pick...

## User

User Request: Can we reliably get the album cover? Even if not, we should pick out a few of the main accent colors from the album art and use that as the background. And we'll just make a UI so no matter what color it is, the text is clearly legible and has enough contrast.
Target GitHub Repository: mattdanielmurphy/music-cross-linker
Please query the GitHub connector for repository source code and documentation for repo 'mattdanielmurphy/music-cross-linker' if needed.

Please act as a senior planner. Analyze the request and output a detailed architectural implementation plan for the orchestrator.

---

## Assistant

## Perplexity — 01:41 AM

Now let's fetch the key files: TrackView.tsx, MatchCard.tsx, PlatformButton.tsx, lib directory, README/AG_CONTEXT for architecture, and app/lib listing.

## Perplexity — 01:41 AM

Now fetching key content files in parallel: TrackView.tsx, MatchCard.tsx, PlatformButton.tsx, odesli.ts, globals.css, README.md, AG_CONTEXT.md.

## Perplexity — 01:41 AM

Architectural Implementation Plan: Dynamic Album-Art Theming for `music-cross-linker`

Based on the repo structure (Next.js app router, `app/lib/odesli.ts`, `app/lib/urlResolver.ts`, `app/components/track-view/*`, Supabase-backed migrations for track fingerprinting), the app resolves a pasted music URL into cross-platform links via the Odesli/song.link API and renders a `TrackView` with per-platform sections (`AppleSection`, `SpotifySection`, `YouTubeSection`) and `MatchCard`/`PlatformButton` components. Album art and color theming need to slot into this existing pipeline without a full rewrite.
github

Reliability of Album Art

Odesli's `linksByPlatform` response includes a `thumbnailUrl` per platform (already surfaced somewhere in `odesli.ts`), but it's not fully reliable on its own: it can be missing for some platforms, low-resolution, or point to a stale/wrong image for compilation albums or singles. Treat art fetching as a **tiered fallback chain**, not a single call:

**Primary**: Odesli `thumbnailUrl` from the highest-confidence matched platform (prefer Apple Music, since its artwork URLs support arbitrary upscaling via `{w}x{h}` template swapping, e.g. rewrite `100x100bb.jpg` to `1000x1000bb.jpg`).

**Secondary**: If Odesli's field is missing/broken, hit Spotify's album `images[]` array (already have `spotify.ts`) or Apple's iTunes Search API `artworkUrl100` (upscale the same way).

**Tertiary**: YouTube video thumbnail (`maxresdefault.jpg` fallback to `hqdefault.jpg`) — lowest quality/least trustworthy since it may be a static "video cover" rather than true album art.

**Final fallback**: no image found → skip straight to a neutral brand gradient (no image-derived colors at all).

This chain should live as a pure function in `app/lib/albumArt.ts` (new file), called once per resolved track and cached — not recomputed on every render or every platform section mount.

Server-Side Color Extraction Pipeline

Extract colors **server-side**, not in the browser, to avoid CORS canvas-tainting issues (many art CDNs block `crossOrigin` canvas reads) and to keep the client bundle light.

Step	Approach
Fetch image	Server fetch the resolved art URL (with timeout + size cap, e.g. 5s/2MB) inside the API route or a server component
Decode/resize	Use `sharp` (already common in Next.js server runtimes) to downscale to ~64×64 before analysis — massively speeds up quantization
Palette extraction	Run a k-means/median-cut quantizer (e.g. `node-vibrant`'s Node build, or a small custom k-means over the resized pixel buffer) to get 4–6 dominant swatches with population weight
Classify swatches	Tag each swatch as `vibrant`, `muted`, `dark`, `light` by saturation/lightness, mirroring Vibrant.js's palette categories, so the UI layer can pick semantically ("give me the dark muted one for background")

Wire this into a new API route, e.g. `app/api/palette/route.ts`, that takes an art URL (or track ID) and returns `{ swatches, background, textColor, accent }`. Cache the result.

Contrast-Safe Theming Logic

The core rule: **never trust the raw extracted color for text** — always derive a guaranteed-legible pairing.

Pick a background from the extracted palette (prefer the `dark muted` or `light muted` swatch depending on overall art brightness — this avoids a background that's just as saturated/loud as the art itself).

Compute relative luminance of that background using the WCAG formula: 
𝐿
=
0.2126
𝑅
+
0.7152
𝐺
+
0.0722
𝐵
L=0.2126R+0.7152G+0.0722B (linearized sRGB).

Choose text color as pure white or pure near-black, whichever yields a contrast ratio 
≥
4.5
:
1
≥4.5:1 (WCAG AA for body text, 3:1 minimum for large headings). If neither pure black nor white clears the bar against a mid-tone background (rare, but possible with mid-gray art), programmatically darken/lighten the background swatch by stepping lightness in HSL until one side clears 4.5:1 — this guarantees legibility even for pathological album art.

Use a second, more vibrant swatch as an `--accent` color for buttons/links, but run the same contrast check against whatever it sits on top of (button background vs. button text) before using it directly — accents get a contrast pass too, not just backgrounds.

Expose the final palette as CSS custom properties (`--bg-primary`, `--bg-secondary`, `--text-primary`, `--text-secondary`, `--accent`) set inline on the `TrackView` wrapper `div`, so every child (`MatchCard`, `PlatformButton`, `LoadingChip`) consumes via `var(--...)` in `globals.css`/component styles instead of hardcoded colors — this is the key refactor since those components currently likely use static Tailwind/CSS colors.

Component & Data Flow Integration

`urlResolver.ts` (or the API route that calls it) should attach the resolved `albumArtUrl` to the track object it already returns, since it's the place that already knows which platform match is highest-confidence.

`TrackView.tsx` becomes responsible for: (1) requesting the palette for the resolved art URL, (2) applying the computed CSS variables to its root element, (3) rendering the art itself with a skeleton/blur-up placeholder while the palette computes (use `PlayerSkeleton.tsx`, which already exists, as the loading state).

Do the palette fetch **in parallel** with the platform-matching calls (Spotify/Apple/YouTube resolution), not after — since both depend on the same initial URL parse, there's no reason to serialize them, keeping perceived load time flat.

`MatchCard`, `PlatformButton`, `AppleSection`, `SpotifySection`, `YouTubeSection` should have their hardcoded background/text color classes removed and replaced with CSS-variable-driven styles so the theme cascades automatically without prop drilling colors through every component.

Caching and Persistence

Since the app already persists resolved tracks in Postgres/Supabase (see `migrations/001_initial.sql`, `003_fix_fingerprint_column.sql`, `004_add_uncertain_manual_match.sql` — the schema already tracks per-track fingerprints and match confidence), extend that same row rather than building a separate cache:
github

Add a migration `005_add_album_theme.sql` with columns like `album_art_url text`, `palette jsonb`, `theme_bg text`, `theme_text text`, `theme_accent text`, `theme_computed_at timestamptz`.

On resolution, check if theme columns are already populated for that fingerprint before recomputing — this avoids re-fetching/re-quantizing the same album art on every repeat visit to a slug, which matters given `slugStore.ts` already implies persistent shareable slugs.

Set a TTL/version flag so you can invalidate and recompute if the algorithm changes later (e.g. bump a `theme_version` int column).

Edge Cases to Handle Explicitly

**No art at all**: fall back to a fixed neutral brand gradient — never show a plain white/black screen.

**Near-monochrome art** (e.g. all-black or all-white covers): the lightness-stepping contrast fallback above handles this, but test it explicitly since it's the most common real-world failure mode for minimalist album covers.

**Animated/GIF or very large source images**: cap fetch size and always downscale before quantizing so a 5000×5000 cover doesn't blow the API route's execution time.

**Slow art host**: set an aggressive fetch timeout on the palette route so a stalled CDN doesn't block the whole `TrackView` from rendering — render with the fallback gradient first, then swap in the computed theme when/if it arrives (progressive enhancement, not a blocking dependency).

---
