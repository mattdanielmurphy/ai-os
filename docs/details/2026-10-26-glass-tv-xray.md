# Glass TV X-Ray

## 15:05 Plan and four design options

Matt asked (on his call with Tyler) for Prime Video's X-Ray in Glass TV: pause and see who's on screen. Amazon's X-Ray data isn't public, so this builds an X-Ray-like overlay from legit data.

---

### Four design options

Made by four separate agents (one brief each, so they don't anchor on each other), all in Glass TV's own look: Schibsted Grotesk + DM Mono, hairline borders, the existing blue accent, light and dark. Page: https://matt-pages.vercel.app/64b2148e-d2a4-4e24-8008-4c3cfed21f8a/ (source `~/projects/pages/site/glass-xray/`).

- A: side rail like Prime, tabs for In scene / Cast / Trivia / Music.
- B: name tags with leader lines on each person; nothing else covers the picture.
- C: liner-notes shelf at the bottom: who's here, footnote trivia ("director's commentary"), music cue, plus a timeline of when each character appears.
- D: nothing on the video; the Glass TV window docks beside IINA and becomes the X-Ray screen, with a "tonight 1 of 2" line.

Mockups are concept-level: trivia, music and "known for" text are marked "Sample:". Known rough edges: A's keycap hints overlap its progress bar; B's leader lines don't land exactly on the faces.

---

### Overlay runs as IINA plugin

IINA 1.5 is installed and supports plugins with an HTML overlay on the video; Matt already runs the skip-intro and OpenSubtitles plugins. X-Ray becomes a small plugin that shows on pause and asks the Glass TV server what to draw. Option D doesn't need the plugin.

---

### Data sources stay legit

- Cast, guest stars and headshots per episode: TMDB episode credits (key already in Glass TV).
- Trivia: Wikipedia/Wikidata. IMDb trivia is skipped: no API, and its terms forbid scraping.
- Music: Chromaprint/AcoustID on a short audio clip at the pause point. ShazamKit was rejected for now (needs an Apple developer entitlement).
- No piracy or debrid sources.

---

### Scene detection scans overnight

"Who's on screen right now" needs face matching. Plan: scan each episode once while the Mac is idle at night, one frame every ~2 s, Apple Vision face detection plus a small face model matched against that episode's TMDB headshots; save a timeline per file. Low priority, one file at a time, because the Mac is low on RAM. Until a file is scanned, X-Ray shows the episode cast list. Rejected: a vision LLM per pause (slow, heavy) and live matching during playback (RAM).

Full plan: `~/projects/glass-tv/docs/XRAY_PLAN.md`. Nothing is built yet; waiting for Matt's pick. Undo: delete the page folder and the plan doc.
