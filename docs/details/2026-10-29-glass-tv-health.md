# Glass TV · playback health (self-reporting, steps 1–2)

## 21:00 Step 1 built; tool choice for step 2

**Asked (from the Glass TV coordinator):** plan and build steps 1–2 of "Glass TV reports its own problems" (VISION.md): a local event log, then sending odd events home; check Sentry / GlitchTip / PostHog first and show Matt the choice.

---

### Step 1 is built

- New `src/health.ts`: one JSON line per event in the data dir (`health.jsonl`), page at `/health` (odd things only; "Show every play" shows all).
- Mac player (`src/player.ts`): per play, time from pressing Play to the first frame, how long finding a source took, buffering stalls (the player's `paused-for-cache`), seconds really watched. One `play` event at the end; odd when the start is over 15 s, 3+ stalls or 20+ s buffering, or it never started.
- Wrong length (the We're the Millers case): file duration vs TMDB runtime (`M.runtime`), odd when 25%+ off. Works for Mac plays and for TV/iPad plays (from their progress reports).
- Errors: no playable source (Mac and TV), video service not answering (TV), TV "stalled, switched source" fallbacks.
- Crashes: macOS crash reports for Glass Player / Glass TV (scanned at start and hourly; older ones ignored), server uncaught exceptions, and TV/iPad crash reports that already arrive at `/tv/v1/errors`.
- Thresholds are tweaks (`health.*`, in the ⌃⌥⌘T panel).
- Privacy: each event has a title-free one-line `msg`; `title`, `key`, `detail` stay local. `forHome()` strips them unless `GLASS_SHARE_TITLES=1`.
- Tested: unit tests (`tests/health.test.ts`), a stand-in server on port 4799 (a fake TV crash and a 22-min Millers file both logged as odd), and the fake player (slow start logged).
- Not live yet: the running Mac server was playing Ted Lasso, so it wasn't restarted. Goes live on the next restart.
- Not covered: the Android/iPad players' own first-frame and stall timing (they'd need to post to the server; follow-up for the Android/iPad sessions).

---

### Tool choice for step 2

- **Sentry (sentry.io):** best crash tooling, SDKs for Android/Swift/Bun. Free plan 5k errors/month. Data leaves to Sentry's cloud; doesn't model "wrong length" or "slow start" trends; the daily triage would need its API.
- **GlitchTip (self-hosted, open source):** Sentry-compatible, would fit on the VPS (24 GB RAM). Another service (Postgres + Valkey + web + worker) to keep alive; same gaps for playback trends.
- **PostHog:** product analytics; self-host needs a big box (ClickHouse, Kafka), cloud sends viewing data out. Overkill.
- **Small collector in Glass TV's own server (recommended):** the server already runs on the VPS (tailnet only) and already receives TV/iPad crash reports. Add one route that takes odd events from other Glass TV servers and one page. Plain JSON lines the daily Claude routine can read directly; titles never leave unless allowed; nothing new to run.
- Rejected doing both: GlitchTip only adds value for native stack traces with symbols, which the current crash reports mostly cover. Revisit if Swift/Kotlin crashes become hard to read.

How to undo: `git revert` the commit; delete `health.jsonl` from the data dir.
