<!-- readthrough project=code -->
# Glass TV reports its own problems

## 23:00 Plan and first case

You asked for a system where every build reports problems, a receiver collects them, and Claude threads investigate so a coordinator can bring you findings. You also asked about We're the Millers.

### Most of it exists

---

Built 2026-10-29 (VISION.md): play log on each server, odd events to the VPS, 9:00 triage, briefs, Coordinator hand-off. The collector is the VPS; Sentry-style tools were rejected earlier. So the plan is to close gaps, not start again.

### Three gaps

---

1. TV and iPad report only source-finding time, fallbacks and crashes, not first frame or stalls. "Streaming got slower" can't see their real playback. Add play reports in PlayerScreen.kt and the iPad player, posted to a new `/tv/v1/health`, and ship new builds.
2. Triage ran at 9:00 today while the Mac server was down, saw 0 events and still moved its "last run" forward, so anything odd from then would be lost. Fix: retry, and if a server stays down, don't advance.
3. Unit tests write fake events to the real log: run together, an earlier test file fixes the data folder before health.test.ts sets its own. Fix: one shared test data folder set in a preload. My run tonight added 3 fake events; I removed those (kept a copy in the session scratchpad). They'd have raised a false alarm tomorrow.

Rejected for now: raw title sharing, Sentry.

### Privacy

---

Titles, keys and crash details stay on the machine that recorded them; only title-free lines go to the VPS, which is tailnet-only. Nothing reveals what your parents or brother watch. Weak spot: crash stack traces are stripped too (`detail`), so a TV crash arrives with only its one-line message, and the investigation needs the local /tv/errors page. Proposed: send stack traces (no titles in them) home. Tell them in one line that the app sends fault reports; the choice is yours.

### Millers case

---

Saved play: `We're the Millers [2013 Blu-ray disc] [2-in-1...]`, 1359 s (22.7 min). A disc holds the film as chunks, so one chunk explains the mid-film start and the short length. Slow load is likely the disc's high bitrate, not measured. isDiscImage matches this name, the live server has had it since 18:36, and quality grading excludes it. Not retested with real streams, to avoid Real-Debrid requests. Play was before the health log, so no event exists. A differently named disc could still slip through; idea: on wrong length, switch source automatically.
