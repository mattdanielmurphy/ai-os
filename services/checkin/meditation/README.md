# Guided audio (meditation, hypnosis)

Voice-over-music tracks for the morning check-in and for winding down. Player page (public, unlisted):
https://matt-pages.vercel.app/3a22db06-7d4d-4779-adde-1e377c22caa3/ (`~/projects/pages/site/still`).

- `scripts/*.txt`: the scripts. Headers pick the Speechify voice, speed and music bed; `[pause N]` = N s of music.
  - `morning-mindfulness.txt`: 10 min, secular attention practice (voice `douglas`, Breath loop).
  - `deep-relaxation-hypnosis.txt`: 22 min, body scan + countdown + safe place + count back up (voice `marian`, Cicada loop).
- `build.py scripts/<name>.txt` → `out/<name>.m4a` + a `.json` with each line's start time. Lines are voiced once and
  cached in `tmp/lines/`, so editing a line re-records only that line. Feel knobs at the top (gap, music level, duck, loudness).
- Music: the long loops in `~/projects/claude-ambient/out/` (real Arturia piano, rendered from code; no AI music).
- To update the page: rebuild, copy `out/*.m4a` into `~/projects/pages/site/still/`, then `pages deploy`.
- The check-in page's Breathe step links the morning track ("Or a 10-minute guided meditation"); a tap saves
  `meditation: true` in that day's page doc.
- Levels (the page's difficulty slider): `levels.py` writes `scripts/level-1..8.txt` (1 to 20 min); build each with
  `build.py`. A steady drone and a bell come from claude-ambient (`# drone:`, `# bell:`); `[fill]` stretches the
  silences to hit `# minutes:`, and `# bell_every:` rings the bell on a steady grid during them.
