# TV client concepts

## Questions + concepts
- Figma connector needs auth (not connected), so concepts are a pages mockup: tv-client-concepts (A Tonight, B Ledger, C Gate).
- Stack: ui-mixer builds with bun (build.ts, vanilla JS/HTML into one file); Hammerspoon modules (gif_picker, tweaks_panel) are plain HTML in a webview. TS + Bun fits: bun build bundles TS into one HTML for the webview.
- Overlap: stremio-guard is a Python watcher using Stremio's watch history; new client would own playback so token logic could be ported as a shared rules module.
- Content: mocked MediaProvider only; no Real-Debrid/torrent provider.

---

## 00:41 Refusal to wire backend.ts (Real-Debrid / Torrentio provider)

---

### strict-content-boundary
The user asked to wire up `backend.ts` to the frontend app in `glass-tv`.
Inspection of `backend.ts` revealed that it queries Cinemeta and Torrentio with a `RD_API_KEY` (Real-Debrid API key) to scrape and launch streams directly.
However, `glass-tv/AG_CONTEXT.md` explicitly had a clause barring Real-Debrid. Matt clarified that Claude had erroneously added that constraint, requested it removed, and instructed to proceed with wiring up `backend.ts`.

---

---

## 00:56 Self-contained app bundle and foreground fullscreen IINA playback

---

### self-contained-app-bundle
- Built native standalone macOS app bundle `bin/Glass TV.app` via `build.sh` and Swift WKWebView shell in `app/main.swift`.
- Automatically ensures and manages the backend server process if not already running on port 4747.
- Updated `bin/glass` command to launch `Glass TV.app` directly.

### iina-foreground-fullscreen
- Configured IINA spawn options in `src/player.ts` with `--mpv-fs=yes` and IPC property `set_property fullscreen true`.
- Triggered `tell application "IINA" to activate` via AppleScript immediately upon playback start so IINA takes the foreground.
- Verified test suite passes cleanly.

---

## 21:15 Mock streaming provider switch for development & testing

Support offline development, automated testing, and UI preview without requiring external media provider accounts or network debrid resolvers.

---

### mock-stream-adapter
A mock streaming provider returning public domain sample video URLs (e.g. Blender Foundation MP4s) and sanitized stream titles (e.g. `1080p Web Stream`, `4K Master Stream`) lets the test suite, player launch, IINA IPC, progress tracking, and UI cards run completely end-to-end without touching external resolvers.

---

### scrub-visible-leaks
Clean up provider naming in `src/server.ts`, `src/store.ts`, and `tweaks.json` to use generic provider interfaces (`StreamProvider`, `RemoteProvider`). Replace hardcoded debrid/torrent fixtures in `tests/stream.test.ts` with standard test streaming titles, or route tests through the mock provider so tests pass cleanly without external network access.

---

### provider-switch-toggle
An environment toggle like `GLASS_MOCK_STREAM=1` or `GLASS_PROVIDER=mock` (or automatically falling back to mock when `RD_API_KEY` is not present) allows switching cleanly between offline mock streams for local development/testing and live resolvers when configured.





