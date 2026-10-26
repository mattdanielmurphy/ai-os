# Glass TV → Android TV (Google TV Streamer 4K)

## 21:49 Plan restated, repo blocked, one boundary

What Matt asked: port Glass TV to Android so it runs on his Google TV Streamer 4K. Shelve the limitation features for now. Home shows only Continue Watching and Library (no "all titles" list, not even behind a toggle). D-pad must control everything. Shows with many seasons must not create a giant horizontal scroller. Minimal, clean, dark only.

---

### repo-not-reachable
This session runs on Matt's Oracle VM, not his Mac. `mattdanielmurphy/glass-tv` was attached, but cloning fails: the VM's `gh` token in `~/.config/gh/hosts.yml` is invalid and there's no session git proxy. Fix: `gh auth login -h github.com` on the VM, or run the thread on the Mac. Nothing was built yet.

---

### native-compose-for-tv
Recommended stack: native Kotlin app with Jetpack Compose for TV + Media3 (ExoPlayer). Why: Compose for TV handles d-pad focus, focus memory per row and the TV focus styling natively; a WebView wrapper of the current web UI would need hand-rolled spatial navigation, which is exactly the "d-pad perfectly" risk. Rejected: WebView wrapper (fast but focus bugs), React Native TV (extra layer, no gain), handing playback to an external player app (an extra app to install and less control over progress tracking).

---

### thin-client-to-backend
The Android app is a thin client: it asks the existing Glass TV backend (port 4747) for Continue Watching, Library, show/season/episode metadata and a playable URL, plays it in Media3, and reports progress back so Continue Watching stays in sync with the Mac. Open choice: backend stays on the Mac (Mac must be awake to watch) or moves to the VPS (always on). Default proposed: Mac for now.

---

### season-layout
Show page: vertical season list on the left (scrolls vertically, any number of seasons), episodes for the focused season on the right as a vertical list. D-pad left/right moves between the two columns, up/down within one. No horizontal scrolling anywhere except the two home rows, which scroll lazily.

---

### client-only-boundary
The earlier details file (2026-10-25-tv-client-concepts.md) shows the live stream resolver (Torrentio + Real-Debrid) was moved into `src/stream_real.ts` and hidden from Claude with `.claudeignore`, and the notes were rewritten to remove mentions of that. I'll build the Android client against the backend's generic stream endpoint, but I won't port that resolver to Android or work around the `.claudeignore` arrangement. Told Matt plainly rather than quietly skipping it.

## 22:05 Building the Android TV frontend

Matt: the GitHub login was fine (it was a stale token on the VM, refreshed now); backend is out of scope. Real-Debrid was only his dummy backend for varied test titles; the real app will play licensed media once deals close. He wants only the frontend. Mid-turn: use the reel explainer's design as the basis. Boundary resolved: I build the client against a mock repository and never touch the `.claudeignore`d files.

---

### where-the-code-lives
`glass-tv/android/` (Gradle project, package `ca.mattmurphy.glasstv`). The Mac web app is untouched. CI: `.github/workflows/android.yml` builds a release APK (debug-signed so it sideloads) on every push to `android/`, artifact `glass-tv-apk`. This VM is aarch64 with no Android SDK (Google's aapt2 is x86-only), so CI is the build machine.

---

### reel-look
Reel 004 uses the `calm` theme (ai-os `services/reels/themes/calm.json`): dark bg #1b1d1e, surface #282a2c, ink #f2f3f3, muted #8f9195, hairline #383a3d, teal accent #4fc3c0. Fonts Big Shoulders Display (condensed uppercase headings), Hanken Grotesk (body), Martian Mono (labels), bundled as variable TTFs. Reel habits copied: pulsing accent dot beside mono labels, "01 — CONTINUE WATCHING" chapter-style labels, hairline-bordered 6dp cards, thick flat progress bars. No orange.

---

### home-layout
Top bar (pulsing dot + GLASS TV, clock), a hero block that shows the focused card's title, meta line and two-line synopsis, then two rows: Continue Watching (16:9 cards with progress bar) and Library (2:3 posters, alphabetical). No other titles anywhere. Continue Watching = in-progress items, plus "Up next" when the last episode of a show finished; finished movies drop off. Back from a title lands on the card you opened (rows keep their scroll).

---

### show-layout
Three columns: info + Play/Resume, vertical season list, episodes. Focusing a season switches episodes (no click needed). Right from seasons lands on the up-next episode; left from episodes returns to the selected season; left from seasons goes to Play. Explicit key handling instead of Compose's focusRestorer because that API has changed shape across releases.

---

### player
Media3 PlayerView (its built-in controls are already d-pad friendly). HLS + DASH modules included, which is what licensed streaming backends serve (and Widevine DRM later). Back hides controls, then exits. Progress saved every 5s and on exit; within 2 min of the end counts as watched. No autoplay of the next episode.

---

### mock-data
`MockRepository`: 12 made-up titles (8 shows, 4 films), including "Harbour Lights" with 24 seasons to prove the season layout. Generated poster art from palette tints; `posterUrl` shows real art via Coil when a backend provides it. Streams are public test streams (Mux BBB HLS, Shaka Sintel/Angel One DASH, Apple bipbop). Seeds four progress entries on first run so Continue Watching isn't empty.

---

### install
`android/install.sh <tv-ip>` downloads the latest CI APK with `gh`, `adb connect`s and installs, then launches. Needs developer mode + USB debugging on the TV (steps in `android/README.md`).

---

### untested
Not run on a TV or emulator yet. CI compiling is the only check from here. Focus behaviour and the look need Matt's eyes on the Streamer.

---

### how-to-undo
Delete `android/` and `.github/workflows/android.yml` in glass-tv; nothing else changed.

## 22:50 Tested on an Android TV emulator; ready to install

---

### emulator-test
Added a second CI job: boots an Android TV (API 34, 1080p) emulator, installs the APK, drives the d-pad with `adb input keyevent` (`android/ci/screens.sh`) and uploads 14 screenshots. Confirmed: home lands on the first Continue card; down/right through Library; opening a 12-season show; seasons scroll vertically and the episode list follows; right lands on episodes, left returns to the selected season; Back returns home with focus kept; a Continue card plays with Media3 controls. No crashes from the app in logcat.

---

### bugs-fixed-from-screenshots
1. Hero synopsis overlapped the "01 — Continue watching" label (hero height 150 → 178dp).
2. After finishing an episode, home had no focused card because the card key changed (S23E6 → Up next S23E7); now falls back to the first card.
3. Mock resume points (18 min) were past the end of the 10-min test streams, so playback ended instantly and marked the episode watched. The player now restarts from 0 when a resume point is past the end. Dropped the 1-minute Angel One test stream.

---

### still-untested
Not on the real Streamer: remote feel, 4K output, HDR, and how the Google TV launcher shows the banner. Media3's stock control bar is unstyled (grey Material look) — a candidate for a themed pass later.
