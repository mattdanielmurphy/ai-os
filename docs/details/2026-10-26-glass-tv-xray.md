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

## 12:30 On-pause recognition instead of overnight scans

Matt rejected overnight scanning: an episode gets paused 0–3 times, so scanning every scene wastes nearly all the work, and it must work with streams too. He wants: on pause, send data to the server, get the answer back. He likes B if it isn't much harder, and wants C kept for a future director's-commentary feature.

---

### Recognise faces only on pause

On pause the IINA plugin grabs the paused frame (a player screenshot, so local files and streams behave the same) and posts it to Glass TV. Apple Vision finds the faces on-device; a small face-embedding model (MobileFaceNet-size, about 15 MB) compares each face with that episode's TMDB cast headshots, whose embeddings are made on the first pause in the episode and cached. Reply: actor, character and a box per face. Aim: under a second, about 100 MB RAM only while it runs.

Rejected: vision LLMs (they usually refuse to name real people from their faces, and cost per call); overnight scans (Matt's reason above). Kept as an optional later booster: AWS Rekognition celebrity recognition, about a tenth of a cent per pause, needs an AWS account (none set up now), better on guest stars.

Untested so far: accuracy of matching one TMDB headshot per actor against a dim, side-on TV frame. Main cast should match well; minor guests may come back "unknown".

---

### Design B is cheap now

Face detection returns a box for every face anyway, so the name tags in B just sit at those boxes after mapping video coordinates to the window (letterboxing included). The extra work is that mapping and keeping tags from overlapping; a plain list stays as the fallback for unknown faces or when no faces are found.

---

### Design C parked in ideas

Added to `~/projects/glass-tv/IDEAS.md` as the future director's-commentary mode, with the mockup link. Plan doc updated: `~/projects/glass-tv/docs/XRAY_PLAN.md`.
