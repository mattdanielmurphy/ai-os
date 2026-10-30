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

## 21:20 Step 2 built: odd events go home to the VPS

- Matt picked the small collector. A server with `GLASS_HOME` appends each odd event (titles, keys and detail stripped) to `health-outbox.jsonl` and posts it to `<home>/health/v1/report`; anything unsent retries every 5 minutes, so an offline TV catches up later. Home dedupes by event id into `health-received.jsonl`.
- VPS: deployed (`deploy/vps.sh`, `GLASS_DEVICE=vps`). Page: http://100.123.57.17:4747/health (tailnet only). JSON for the daily routine: `/health/v1/events?since=<ms>&all=1`.
- Tested end to end: a stand-in server sent a fake 22-minute We're the Millers file; it showed on the VPS as "tv parents movie: file runs 22 min, catalog says 110 min" with no title. That test event stays on the VPS page.
- Mac: launchd plist now sets `GLASS_HOME` + `GLASS_DEVICE=mac`. Not restarted (Ted Lasso was playing); `tmp/health-go-live.sh` (detached) runs `./install.sh` once nothing has played for 10 minutes straight, gives up after 8 h. Log: `tmp/health-go-live.log`.
- Step 3 plan written in VISION.md.
- Not done: Android/iPad player-side first-frame/stall timing; the parents' server needs `GLASS_HOME` too when it exists.
- Undo: `git revert bdefb52 cecb78a`, `deploy/vps.sh`, `./install.sh`.

## 21:40 Step 3 built: daily check opens investigations through the Coordinator

- `bin/health-triage.ts` + `src/triage.ts` (glass-tv 833f9e9), launchd `ca.mattmurphy.glass-tv-health-triage` daily at 9:00 (installed; also in `install.sh`). Log: `~/Library/Logs/glass-tv-health-triage.log`.
- How it works: reads `/health/v1/events` from the Mac and the VPS (35 days), groups odd events since the last run by kind + screen + message (numbers blanked), adds "slower this week" trends (7-day median start/find time 50%+ above the 4 weeks before, 5+ plays each). New = not reported in 14 days; worse = 3x the count when reported. Up to 3 a day get a brief in the Glass TV data dir `health-triage/` (titles readable there, never leaves the Mac); the rest are listed. Queues one message via `coordinator_inbox.py put`; the Coordinator starts one fresh glass-tv worktree session per brief and tells Matt. Quiet days send nothing.
- Why the Coordinator, not `claude -p` from launchd: a scheduled script can't open a visible Code-tab thread; the inbox is how other scripts already hand work to the Coordinator, and it already knows how to start sessions and tell Matt.
- Tested: unit tests; dry run with test events (made the brief for the fake Millers event); a harmless test message reached the Coordinator (delivered within 45 s).
- Not tested: a real 9:00 run with a real problem, and whether the Coordinator starts sessions from an inbox message or only proposes them (the app may hold automated starts as proposal cards).
- Trends only see the full play history of servers that record plays themselves (the Mac today); other servers send only odd events.
- Undo: `launchctl bootout gui/$(id -u)/ca.mattmurphy.glass-tv-health-triage`, move its plist to ~/.Trash, `git revert 833f9e9`.
