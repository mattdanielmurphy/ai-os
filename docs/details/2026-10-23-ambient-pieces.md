# More ambient pieces (Augmented Grand + FabFilter)

## 07:55 Piece 2: piano-airports-02

What was asked (coordinator relay): more pieces in the style of piano-airports-01, through the offline
renderer in `~/projects/claude-ambient`, mixing Augmented Grand presets, FabFilter where possible,
always Pro-R for reverb, one at a time, reveal the first in Finder after claude-control clearance.

---

### Preset loading works offline

Arturia presets are text "boost serialization" archives in
`/Library/Arturia/Presets/Augmented GRAND PIANO/Factory/Factory/` (301 presets). The AU's
`fullState["Controller State"]` holds exactly that archive (the default is Kairos, which is what
piano-airports-01 used). Swapping in another preset file's bytes loads it: parameters change and
the state reads back with the new name. No GUI needed.

---

### New multi-track renderer

`render_mix.swift` (new file; `render.swift` untouched since the Cardinal thread owns it). Each track:
an Augmented Grand instance with its own preset, instrument params by name, a FabFilter FX chain,
gain/pan/send. All tracks feed a dry bus plus a send bus into one FabFilter Pro-R 2 (100% wet),
then Pro-L 2 on the master. Arturia's own reverb macro is set to 0 on every track so Pro-R is the
only reverb. 8 s warm-up so samples load. Peak memory ~1.2 GB with three instances, ~70 s to
render 4 minutes. It also counts fully silent blocks (dropout check): 0.

---

### The piece

`pieces/airports_02.py`, E-flat major, Eno phasing loops (loop lengths 19.7-47.9 s, none divide):
- piano: **Intima**, Pro-Q 4 low cut 90 Hz, Saturn 2 Clean Tape light drive, 4 voices of 1-3 notes.
- pad: **Breath of Light**, Pro-Q 4 low cut 45 Hz, slow low Eb/Bb/Ab tones, -8 dB.
- air: **Cotton Wool Worlds**, Pro-Q 4 low cut 300 Hz, Timeless 3 ping-pong delay, high notes, -12 dB.
- Pro-R 2: Space 0.78, Brightness 0.38, Modern.
Balanced by soloing each track (LUFS: piano -32, pad -30, air -31 before gains). 4:16 long,
normalised to -20 LUFS, LRA 7.2. Output `out/piano-airports-02.m4a` (gitignored).
Rejected: Crystal Fairies (chord/sequence preset adds its own notes).

---

### Untested

I can't listen. Only levels, peaks and dropouts are checked; whether the presets blend well is Matt's call.

---

### Clearance

claude-control ask (light, ticket t2) granted, revealed the file in Finder, then `done t2`.

Undo: move `out/piano-airports-02.m4a` to Trash; the two new files are isolated.

## 08:05 Piece 3 + mixing fix

---

### Gain and send bug

Per-track gain, pan and reverb send were silently ignored: AU effect nodes don't return a mixing
destination, so every track went in at full level and full reverb send. Piece 2 v1 was therefore
wetter and less balanced than planned. Fixed in `render_mix.swift` with a fader mixer per track and a
send-fader mixer into the Pro-R bus; solo loudness now moves with gainDb. Piece 2 re-rendered over the
same file with corrected gains (pad -6, air -7).

---

### Piece 3: piano-airports-03

`pieces/airports_03.py`: A-flat major / F minor, 5 piano voices (loops 18.3-38.9 s).
- piano: **Ice Piano**, Pro-Q 4 low cut, Saturn 2 Clean Tube.
- pad: **Alpha Orionis** (slow attack ensemble), -9 dB.
- air: **Glassy Keys**, Timeless 3 longer ping-pong delay, -6 dB.
- Pro-R 2: Vintage style, Space 0.85, darker (Brightness 0.3).
4:16, -20 LUFS, 0 dropouts. Not listened to by me.

## 08:15 Piece 4: piano-airports-04

`pieces/airports_04.py`: D lydian, slower and sparser (piano loops 21.1-41.7 s, pad up to 59.9 s), 4:46.
- piano: **Darker Pools** (granular piano), Pro-Q 4, Saturn 2 Clean Tube.
- pad: **Fading Outward**, Pro-Q 4, Saturn 2 Warm Tape, -6 dB.
- air: **Echo Dust** (slow attack), Timeless 3 ping-pong, +3 dB (it's quiet by nature).
- Pro-R 2: Modern, biggest room so far (Space 0.9, longer decay).
-20 LUFS, 0 dropouts. Not listened to by me.
