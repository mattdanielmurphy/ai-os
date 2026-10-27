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

## 13:05 Design B built and live

Matt 👍'd building B with recognition only on pause.

---

### X-Ray works in IINA

Tested inside the real IINA with a short muted clip made from TMDB stills of The Office S2E1: pausing on Pam and Jim put "Pam Beesly / Jenna Fischer" and "Jim Halpert / John Krasinski" tags on them within about a second, and playing again hid them. Glass TV's live server runs the new code (reinstalled with `./install.sh`).

How it works: the plugin (`iina-plugin/`) asks `127.0.0.1:4747/api/xray?t=<paused time>`. The server saves the paused frame through IINA's player socket, `bin/xray-faces` (Apple Vision) finds faces and makes aligned crops, SFace turns each into a fingerprint, and each is compared with that episode's TMDB cast photos (up to 3 per actor, top 20 billed). One face and one actor are paired at most once, best scores first.

Speed and memory: about 0.1 s per pause once the episode's cast is fingerprinted. That happens in the background when an episode starts (about 3 s, once per actor ever, saved on disk). The model uses about 120 MB only while in use and unloads after 5 idle minutes.

Accuracy on the 4 stills: every named face was right (Michael 0.62–0.64, Pam 0.56, Jim 0.36–0.41). A screaming, blurred Pam and two small background faces came back unknown. Nothing was named wrongly.

---

### What's not tested yet

- Tab, Return and X were tested only in a browser copy of the overlay, not by pressing keys in IINA (that would mean typing on Matt's Mac).
- Only a local file was tried, not a stream. It should behave the same, since the frame comes from the player either way.
- The photo in the Return card loads from TMDB; not checked inside IINA.

---

### Choices and why

- Face model: SFace from OpenCV's model zoo, chosen because it's Apache 2.0 (fine for the world). InsightFace's models were rejected: research-only licence.
- Face finding: Apple Vision (built into macOS, no download).
- Rules for naming a face, all in the Tweaks panel: likeness 0.36 or more, or 0.28 or more and clearly ahead of the next-best actor by 0.08.
- Tags go above the head (a third of a face above the brow line), or under the chin when there's no room; overlapping tags get nudged apart.
- Light and dark follow the system.
- Just for Matt for now: it needs Glass TV, IINA and a free TMDB key.

Undo: `iina-plugin unlink`, `defaults delete com.colliderli.iina PluginEnabled.ca.mattmurphy.glass-tv.xray`, and revert commit 7ef031e in glass-tv.
