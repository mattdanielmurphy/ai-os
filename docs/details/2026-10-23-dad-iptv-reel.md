# Dad IPTV explainer reel

## 22:58 Reel 04 built and published
- Asked: pros/cons of a Telus-replacement IPTV Firestick for Dad, plus alternatives, as an explainer reel.
- Made: `services/reels/reels/004-dad-iptv/` (8 slides, Pandora/Gemma/Maeve, panel theme, Piano Airports 04 bed). Headless test passed: no errors, no flash, fits.
- Published: https://claude.ai/artifact/URKDnBH2RXXKa9QzwXBQqf (private; share from the page's Share menu).
### Legal framing
Selling: clearly illegal. Courts ordered ISP blocking (GoldTV 2019, upheld 2021). Watching: "grey zone, not clearly safe", lawyer suggested. I left out the unverified "$5,000" damages figure.
### Prices (searched Oct 2026, secondary sources, verify)
Sportsnet+ Standard $34.99/mo or $269.99/yr; Crave $11.99 with ads, $22 premium; Netflix with ads $7.99; Prime $99/yr; Apple One from $22.95/mo. Telus ~$75/mo = $900/yr (Dad's number).
### Flags
- Dad's "$350/yr" for the remaining subs looks low against list prices (Sportsnet+ alone ~$270). Shown as "Dad's own count".
- OTA and free CBC hockey streams rest on older sources; slide says "check which games". Edmonton channels not confirmed. Pluto/Tubi in Canada unconfirmed, not mentioned.
- Domain age, refund policy, channel count labelled unverified. No setup/upstream info included.
- Not eyeballed slide by slide; text widths checked by script only.
Undo: delete the reel folder and the artifact.

## 23:40 Rebuilt after Matt's feedback
- Dropped: legal/grey-area slide, quality talk, antenna and generic free apps, any mention of "Dad". Pandora only.
- Added: before-costs breakdown (Telus $900, Sportsnet+ $350, others ~$750 estimate = ~$2,000, ~$1,100 now), four options with totals (A keep ~$1,100; B box+apps $900–1,150; C box only $150–400; D trim+Plex ~$620), "will it just work / you are tech support" slides, Plex slide.
- The ~$750 "everything else" and D's ~$375 (half of it dropped) are my estimates from Matt's "$2k"; slide says so.
- Plex facts (free, ads, hundreds of live channels, tens of thousands on demand, Bell Media's CTV News and TSN The Ocho, no NHL) come from secondary sources; channel count varies 250–600+. "Runs on Fire TV, Roku, smart TVs" is general knowledge, not searched.
- Still mentions in one line that the streams are unlicensed (it explains why it can vanish). Remove if unwanted.
- Pauses: build.py now joins beats with "..." lines and narration uses " ... " between phrases; captions strip them. Gaps measured at 0.4–0.6 s (Deepgram caps pauses), so cuts sit mid-gap with ~0.25 s margin each side. If word ends still clip, next step is cutting nearer the next word's start.
- headless_test.cjs: skips the voice-switch check when only one voice.
Undo: git revert this commit.

## 23:30 Player fixes
- Crawling last pixels: caused by the slow whole-slide "drift" zoom (scale 1.03 over the beat, linear). Removed it from template.html for all reels.
- Linger on slide: new tweaks beat.holdBase (0.8 s) + beat.holdPerText (0.12 s per text line on the slide) added to the gap before advancing. Busy slides wait ~3-4 s. Tune in the Tweaks panel; rebuild to bake.
- Back arrow while playing now pauses (no auto-advance) until Play is pressed. Next arrow unchanged.
- "Reel 04" removed from eyebrow and slide 1.
- Untested by ear/eye; headless test passes. Undo: git revert.

## 23:45 Slide progress line
- Added a thin line along the bottom of the stage that travels left to right over each slide (voice + pause + linger), so a lingering slide never looks finished. Pauses when paused, resets per slide, empty when not playing. In template.html (all reels). Untested by eye. Undo: git revert.

## 23:52 Last slide wording and box
- "Month to month, a backup for game nights" was unclear. Now: pay month to month (not for a year) and keep another way to watch hockey in case it stops working. Two lines, box resized so padding is even. Narration updated to match. Untested by eye.

## 00:05 Softer colours, one-time vs yearly
- New theme themes/calm.json (this reel only): same fonts and neutrals as panel, status colours and tints softened (pastel green/red tints, muted green/red/blue). Derived from panel, no new hues.
- Costs now split: PER YEAR total plus ONE-TIME line per option. Box (Firestick) ~$50-100 is MY estimate; the yearly service range $150-400 is the brief. Real bundle price ($260-320 per brief) unchecked, so slide says check it.
- Looked at slides 3 and 8 in headless screenshots; fit OK. Undo: git revert.

## 00:20 Voice takes instead of a regen button
- A published page cannot call Deepgram (no key in the page, no backend), and a regen done in a viewer's browser could never reach someone you share with. So: build.py now bakes N independent takes per voice (reel.json "takes": 3; pace nudged 1.15 / 1.18 / 1.12 so Deepgram does not return the same audio). The Voice button (V) cycles them.
- Sharing is exact: the first take baked is the default for every viewer. build.py scores each take by how much of the script speech-to-text heard (all three ~97-98
## 00:20 Voice takes instead of a regen button
- A published page cannot call Deepgram (no key, no backend), and a regen in a viewer's browser would never reach whoever it is shared with. So build.py now bakes N independent takes per voice (reel.json "takes": 3; pace nudged 1.15 / 1.18 / 1.12 so Deepgram returns different audio). The Voice button (V) cycles them.
- Sharing is exact: the first take baked is the default for every viewer. build.py scores each take by how much of the script speech-to-text heard (all three ~97-98 percent, so it barely separates them; glitches are likely audio artifacts it cannot hear).
- To lock a take: tell me which; I rebuild with it first and republish the same link. A true in-page regen needs a small server holding the Deepgram key; not built.
- File is ~7 MB. Undo: set takes back to 1.

## 00:35 Reveal paced to the narration
- Cause: parts appeared at most 0.9 s apart and over only 55 percent of the voice, and rows came in pairs, so slides filled in 1-2 s while the voice ran ~10 s.
- Fix: tweaks reveal.spread 0.55 to 0.85 and reveal.maxGap 0.9 to 4 (all reels); in this reel each row/card is its own reveal group (slides.py g() splits at row()). Items now arrive evenly across ~85 percent of the narration.
- Not synced to the exact words (no word-to-item mapping); even spacing only. Untested by eye/ear. Undo: revert tweaks.json values.

## 00:45 Visuals earlier than the voice
- Voice led the visuals. New tweak reveal.advance (0.75 s, range 0-2): every slide part after the first appears that much earlier (clamped at 0). Matt asked 0.5-1 s; took the middle. Tune in the Tweaks panel and rebuild.
- Untested by ear/eye. Undo: set reveal.advance to 0.
