# Cool GIF sources (2026-10-22)

## 17:55 Sources and options

**Asked:** find existing sources/apps that serve cool, funny GIFs instead of Facebook-style ones; propose 2–3 options, one a small build; log the idea. Build nothing until 👍.

---

### Sources found

- **[The Finer Gifs Club](https://thefinergifs.club)**: small hand-curated collection, the closest thing to "taste" in a GIF library. Searchable inside the Raycast extension below.
- **[r/HighQualityGifs](https://www.reddit.com/r/HighQualityGifs/)**: hand-made, often absurd reaction GIFs; the best "cool not corny" source on Reddit.
- **[r/reactiongifs](https://www.reddit.com/r/reactiongifs/)**: classic reaction GIFs, upvote-filtered by people who share your humour more than Giphy's algorithm does.
- **[r/BetterEveryLoop](https://www.reddit.com/r/BetterEveryLoop/)** / **[r/perfectloops](https://www.reddit.com/r/perfectloops/)**: weird/beautiful loops, more "cool" than "reaction".
- **[Klipy](https://klipy.com)**: Tenor's replacement (ex-Tenor team; WhatsApp uses it). Same mainstream flavour as Giphy, but bigger pool.
- **[Giphy](https://giphy.com)** / **[Tenor](https://tenor.com)**: the Facebook-GIF problem itself. Tenor's API shut down 2026-06-30 (site still up).
- **[Coub](https://coub.com)**: funny video loops with sound; not GIFs, good for weird clips.

---

### Installed tools

- Matt has [Raycast](https://www.raycast.com) and Alfred 5. No GIF extension/workflow installed in either.
- His `gif-search` skill uses the Tenor API, which is dead since June 2026. Flagged, not fixed (out of scope).

---

### Option 1 recommended

**Install [Raycast GIF Search](https://www.raycast.com/josephschmitt/gif-search)** and default it to The Finer Gifs Club; star good finds so they become his own stash. Zero build, free, Klipy now needs no key (routes via Raycast's proxy since July 2026). Why first: existing tool, already in his launcher, 2 minutes.

---

### Option 2 small build

**"Cool GIFs" picker** (Raycast script command or Hammerspoon chooser): pulls the week's top posts from r/HighQualityGifs + r/reactiongifs + Finer Gifs Club, search by title, Enter copies the GIF, ⌘S stars it to a local stash. ~a few hundred lines; Reddit's public JSON works without a key but can rate-limit. Just for Matt, not for the world (Raycast extension already covers the public case). Clipboard use must go through `claude-control lock` only if it runs on its own; a key he presses runs immediately.

---

### Option 3 stash only

**Personal stash**: a folder of GIFs he collects (from Reddit/Finer Gifs), searched by filename in Raycast/Alfred file search. Nothing to build, but grows slowly.

### Rejected
- Building a full GIF app/library from scratch: scope creep; options 1–2 cover it.

## 18:30 Built the GIF picker

**Asked:** Raycast is on the way out, so no extension; build a small QOL utility for the suite. Also: the "avoid new projects" rule is gone.

---

### Picker how it works

`~/.hammerspoon/modules/gif_picker.lua` + `gif_picker.html`, hotkey ⌃⌥⌘G (was free; ⌃⌘G is thread search). A standard window (move, resize, frame remembered, Esc closes). Feed: Reddit's public RSS for `r/HighQualityGifs+reactiongifs` (top this week / top all time; Return = Reddit search across those subs). No API key. Parsed in Lua (`M.parseFeed`), cached in `~/Library/Caches/MDMA/gif-picker/` for 60 min. Click copies: downloads the full GIF, puts both `com.compuserve.gif` data and a file URL on the clipboard, so Messages/Slack/Discord paste it animated; the window closes. ☆ stars into `~/Library/Application Support/MDMA/gif-picker/stars.json` (Starred tab). Knobs in ⌃⌥⌘T: subreddits, cache minutes, tile width, close-after-copy, cache days.

Why Hammerspoon + webview: GIFs animate natively in WebKit, and the suite already has the same window pattern (Tweaks panel); a Swift app would be more code for no gain. Colours: CSS system colours only (Canvas, AccentColor, GrayText), so no invented colours and light/dark both work.

Just for Matt, plus Tyler via the shared suite (added to `suite.SHAREABLE` and UTILITIES.md; no Matt paths).

---

### Picker what was tested

- `lua tests/gif_picker_test.lua`: 34 GIFs parsed from a real feed, escaping, URLs. Suite and slot tests pass.
- Opened it on Matt's screen (clearance granted): grid loads real GIFs, hints visible.
- Copy: clipboard got `com.compuserve.gif` + `public.file-url`; window closed.
- **Untested:** actually pasting into Messages/Slack; starring by click; dark mode look; Reddit search with Return.

### Picker risks
- Reddit rate-limits keyless requests (saw 429 while testing). The cache covers it; on an error the last copy shows with a note.
- Rejected: Klipy/Giphy (need a key and serve the bland mainstream stuff), Finer Gifs Club (The Office only).

### Rule change
`.rules/core_safety.md` rule 1 now says new utilities are welcome; flag only rabbit holes. 1a: found tools are ingredients, no Raycast/Alfred extensions. Same in `~/.claude/CLAUDE.md` and the existing-tools memory. Undo: `git revert` the rules commit.

## 18:55 Picker rework after feedback

**Asked:** no post text, no duplicates, less lag, better GIFs, search all time and beyond two subreddits, a real curated collection, and a window that stands out from white windows behind it with reliable resize edges.

---

### Curated source found

**[Are.na](https://www.are.na)** channels: people with taste hand-collect GIFs there, and the public API needs no key. Default channels: gif-stash (Gif Stash), crazy-cool-gifs, gif-t, zoracle-gifs, gifs-for-future-viewing, another-gif-channel, gif-collection, reactions. Synced once a day (5 pages of 100 per channel), GIFs over 6 MB skipped, de-duplicated: ~2,300 unique GIFs. Dropped retro-gifs and old-web-gif after seeing them (GeoCities clip art). Are.na's Cloudflare returns 403 to browser-looking user agents from scripts, so the picker sends its own name.

Checked and rejected: Are.na block search (403 without login), GitHub GIF repos (jglovier/gifs is small and its tree API returned nothing), replygif.net (no response), GIFCities (GeoCities clip art), Klipy/Giphy (keys + mainstream taste), Finer Gifs Club (The Office only).

---

### Rework what changed

- **No text:** captions gone; hover shows only ☆ (star) and ↗ (go to the source).
- **No duplicates:** same file URL or same byte size counts as one GIF, across all sources.
- **Less lag:** uniform tiles, 24 added per scroll step, only 4 downloading at once, only GIFs near the viewport load, and GIFs scrolled far away unload (all three are knobs).
- **Search:** Return searches the curated library (titles/filenames), stars, and 8 GIF subreddits, all time, by relevance. Imgur links dropped (many show imgur's "no longer available" image).
- **Tabs:** Curated (default, shuffled daily, ⤮ Shuffle) · Reddit best (all-time top) · Starred.
- **Window:** standard macOS window shadow on (Hammerspoon webviews have none by default, which is why it blended into Claude behind it) and a tinted toolbar.

---

### Rework tested and untested

Tested: unit tests (parsers, dedupe, shuffle, search matching), library sync (2,375 GIFs before dropping two channels), screenshots of the Curated grid and a "dancing" search (35 results), window shadow visible.

**Untested:** whether resize edges now feel reliable (needs Matt's hands), real lag on his machine, paste into Messages, dark mode.

**Focus note:** during testing the window took keyboard focus each time it appeared; the search box showed "Oo", which may have been Matt's typing landing there.

---

### Audience areas idea

Matt (2026-10-22): the GIF you'd send a good buddy is different from one you'd send your mom; separate "Areas" with different audiences and vibes. Recorded in IDEAS.md as a future enhancement, not built.
