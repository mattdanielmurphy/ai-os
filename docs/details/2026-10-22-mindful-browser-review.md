# Mindful Browser review (2026-10-22)

## 10:58 What it is and quick wins
**Asked:** Matt linked a claude.ai chat ("Browser to curb social media addiction") and said the project was already started in Antigravity; pull it up and improve it.

**Did:** Read the chat in Chrome. Coordinator guessed it was the wake-up call; it isn't. Found the code at `~/projects/mindful-browser` (repo mattdanielmurphy/mindful-browser, last commit 2026-08-19, tree clean). Read AG_CONTEXT, DEVELOPMENT_JOURNAL, HANDOFF, latest agent log, grepped Sources/Scripts.

---

### What exists
SwiftUI + WKWebView iOS container that opens Instagram mobile web. Built: "use the app" banner/modal suppression, universal-link breakout guards, Accounts Center close fix, ad blocking (content rules + DOM + fetch/XHR feed pruning), Safari extension that bounces instagram links into the app, simulator hot-reload dev loop (`bun run dev`). ~2.4k lines.

### What is missing
The actual product idea: no friction ladder, no usage tracking, no grayscale/latency, no Reels hiding, no onboarding. Grep for friction/grayscale/usage/reels in Sources and Scripts found nothing (only a 250ms empty-batch throttle in network-interceptor.js). It is an ad-blocked Instagram today.

---

### Wins ranked
1. **Usage log + hide Reels day one.** Record minutes per day in the app (UserDefaults/JSON). Hiding Reels was day-one in the chat. Everything else (thermostat, weekly "you used it 20% less" note) needs this data. Small: one Swift observer + a CSS rule.
2. **First friction lever: slow desaturation.** CSS `filter: saturate()` scaled by days since install (e.g. 100% → 60% over 4 weeks). One number fed into the existing injected CSS.
3. **Onboarding screen.** One page: delete the Instagram app, set no limits, trust us; "advanced settings, we recommend you never open this."

Rejected for now: thermostat zones and rage telemetry (need weeks of usage data first), substitution cards (needs a content pipeline), Photon iMessage bot (separate project).

### Untested
Did not build in Xcode; last build state from August is unknown. Instagram web DOM may have changed since, so suppression selectors may need a pass.
