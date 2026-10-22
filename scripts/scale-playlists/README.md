# Scale practice playlists (Apple Music)

Builds the `🎹 Scale Practice` folder in Music: one playlist per key (D, B♭, A, E♭ major)
and per mode (Aeolian, Mixolydian, Dorian, Lydian) from Matt's Favourite Songs, with
keys from Hooktheory TheoryTab (human transcriptions). Each track's Comment gets `Scale: …`.

Run from this folder (writes to ../../tmp/):
1. Dump favourites: see `make_playlists.py` header / earlier `fav_all.txt`, `fav_pid.txt` (osascript over "Favourite Songs").
2. `python3 lookup_keys.py ../../tmp/scale_all.txt ../../tmp/scale_ht.jsonl ~/.hammerspoon/bin/song-key` (6 threads, ~5 min for 3.4k songs).
3. `python3 select_songs.py` → `../../tmp/scale_playlists.json` (only songs with one key across all sections).
4. `python3 make_playlists.py && osascript ../../tmp/scale_make.applescript` (pure AppleScript, no UI input).
5. Catalog tracks can't be added by AppleScript and computer use is blocked for Music:
   add the 4 albums listed in `add_backing.applescript` to the library by hand, then `osascript add_backing.applescript`.
