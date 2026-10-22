# Scale practice playlists (Apple Music)

## 23:59 Playlists built

**Asked:** Apple Music playlists for learning scales and modes (D and B♭ major first; modes Ionian, Aeolian, Mixolydian, Dorian, Lydian; next A and E♭), songs whose key/mode is known, from favourites plus blues/ragtime backing tracks, scale in each song's note.

---

### Eight playlists are live

Folder `🎹 Scale Practice` in Music: D major (20), B♭ major (20), Aeolian (22), Mixolydian (22), Dorian (22), Lydian (6), A major (20), E♭ major (14). Each playlist's description lists the scale's notes or formula. Each track's **Comment** now reads `Scale: D major (Ionian)` etc. (appended after any existing comment; tracks that already had a `Scale:` note were left alone). Order: most-played first, so you start with songs you know. Mode playlists start with the modes that share D major's notes (B Aeolian, E Dorian, A Mixolydian, G Lydian); Dorian starts with Oye Como Va and Chameleon.

---

### How keys were chosen

All 3,454 Favourite Songs were looked up on Hooktheory TheoryTab (human transcriptions, key + mode per section) via `~/.hammerspoon/bin/song-key`'s Hooktheory function. About 1,000 had a transcription. Only songs where **every section is in the same key** were kept; songs that change key were dropped. AcousticBrainz (machine guesses) was not used, it's too unreliable for this. Risk: Hooktheory is user-made, so an occasional song can be off. Lydian is thin because few songs are truly Lydian.

---

### Song key HUD bug fixed

Hooktheory writes flat keys as "E ♭ Dorian" with a space; `song-key` couldn't parse that, so every flat/sharp-key song was missed (B♭ and E♭ came back empty). Fixed the regex in `~/.hammerspoon/bin/song-key` (committed 8574d2a), which also fixes the live Song Key HUD. Cleared its lookup cache so songs re-check (backup in Trash as `song_key.json.bak`).

---

### Backing tracks need four taps from you

Apple Music catalog songs can't be added by script, and computer use is blocked for the Music app by policy. So the two backing playlists exist but are empty: `🎹 Blues & Ragtime` and `🎹 Modal backing (D & A)`. Add these albums to your library (+ button), then I run `scripts/scale-playlists/add_backing.applescript`:
- Modal Backing Tracks - D: https://music.apple.com/ca/album/1268259828
- Modal Backing Tracks - A: https://music.apple.com/ca/album/1278264129
- Blues Backing Tracks: https://music.apple.com/ca/album/1451738265
- 30 Greatest Scott Joplin Ragtime Piano Pieces: https://music.apple.com/ca/album/1213701636

It picks D, B♭, A and E♭ 12-bar blues (shuffle + slow), Joplin rags in B♭ → E♭ (Pineapple, Fig Leaf, Searchlight, Sunflower Slow Drag, Sugar Cane, Peacherine) plus The Entertainer and Maple Leaf, and the 7 modal vamps for D and A (e.g. "Dorian - E min 7 - D" = E Dorian on D major's notes). Rag keys are from Hooktheory (they change key at the trio; the Comment shows both).

---

### Undo

Delete the `🎹 Scale Practice` folder in Music. Comments: search tracks whose comment contains "Scale:". Scripts and how to rerun: `~/projects/ai-os/scripts/scale-playlists/README.md`.
