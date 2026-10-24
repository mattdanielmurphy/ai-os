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

## 08:30 Long morphing loops

Matt liked all four pieces and asked for long (~20 min) loops that morph a lot but loop cleanly, at an
interval with a mathematical or biological meaning.

---

### How the loops stay seamless

Every voice repeats a whole number of times per loop (period = L / count, same jitter each pass) and
every automation is a sine with whole cycles per loop, so the score at t and t + L is identical.
The renderer plays two loops plus 20 s; `loop_finish.sh` keeps the second loop (it already carries the
first loop's reverb and delay tails) and cross-fades its first 6 s with the audio just after 2L, so the
end flows into the start. Gain is one static value (to -20 LUFS, capped at -1 dBFS peak); a limiter was
rejected because its state at the file start broke the seam (measured: seam jump 20x a normal sample
step with it, equal to a normal step without). Output is 24-bit FLAC (gapless; AAC adds padding).

---

### Morphing

`render_mix.swift` gained periodic automation: Augmented macros (Morph, Color, Motion), Saturn drive,
Timeless feedback, track gain and reverb send, and Pro-R Brightness/Decay/Space. Two pianos cross-fade
over each loop; harmony moves through 6 or 8 chords per loop.

---

### Loop 1: Cicada (22:06)

L = 13 x 17 x 6 = 1326 s. Periodical cicadas emerge every 13 or 17 years; prime cycles keep predators
from syncing. Voices repeat 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59 times per loop (all primes).
Presets: Intima + Ice Piano (cross-fading), Breath of Light pad, Cotton Wool Worlds, Glassy Keys + Timeless 3.
D-flat major, 6 chords of 221 s (13 x 17) each.

---

### Loop 2: Sunflower (21:00)

L = 21 min. Sunflower seed spirals come in neighbouring Fibonacci numbers; voices repeat 8, 13, 21, 34,
55, 89 times per loop; tracks are panned a golden angle apart; 8 chords. Presets: Firefly Felt + Darker
Pools (cross-fading), Alpha Orionis pad, Honey Mist, Echo Dust + Timeless 3. A major, leaning lydian.

---

### Untested

Not listened to by me. Morph/Color macros do different things per preset, so some passages may get odd.

## 08:20 Loop: Breath (piece 4 as a loop)

Matt liked piece 4's sparseness and asked for a loop of it, fast. `pieces/loop_breath.py`: L = 1200 s =
120 breaths at 6/min (0.1 Hz coherent breathing, the baroreflex resonance). Same presets/FX/room as
piece 4 (Darker Pools, Fading Outward + Saturn tape, Echo Dust + Timeless 3, big Pro-R), D lydian over
5 chords of 240 s, voices repeating 13-59 (prime) times per loop, macros/gains/Pro-R drifting.
Rendered alongside the Cicada loop to save time (9 min). Seam checked: jump at the wrap equals a normal
sample step. -20 LUFS, 24-bit FLAC, 167 MB. Revealed in Finder after claude-control (ticket t4).
Skipped the per-track balance test for speed (gains taken from piece 4). Not listened to by me.

## 08:35 Loop: Cicada done

`out/loop-cicada-22m06s.flac`, 22:06, seam checked (wrap jump = normal sample step). 13:40 to render.
Its peaks capped the gain at +9.8 dB, so it sits near -23.6 LUFS, about 3.6 dB quieter than the others.
Sunflower render started right after. Not listened to by me.
