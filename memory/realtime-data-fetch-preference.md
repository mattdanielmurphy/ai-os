---
name: realtime-data-fetch-preference
description: Always use WebFetch over WebSearch for real-time data like weather, stocks, or live conditions
metadata:
  type: feedback
---

When the user asks for **current real-time data** (weather, stocks, prices, air quality, etc.), **DO NOT** rely on WebSearch summaries — those can hallucinate plausible-looking but completely wrong numbers.

Instead, use **WebFetch** to pull data directly from an authoritative source. For weather specifically, good sources are:
- `https://www.theweathernetwork.com/ca/weather/...` (Canadian locations)
- `https://wttr.in/<location>` (simple terminal-friendly weather)
- `https://weather.gc.ca/` (Environment Canada)

**Why:** WebSearch AI-generated summaries for time-sensitive live data frequently fabricate realistic-looking readings. WebFetch reads the actual published page content.

**How to apply:** Any time "current" or "right now" or "today's" real-time data is requested (weather, stocks, crypto, gas prices, etc.), skip WebSearch and go directly to WebFetch on a known authoritative URL. When unsure of the URL, use WebSearch to *find* the right site, then WebFetch to get the actual data.